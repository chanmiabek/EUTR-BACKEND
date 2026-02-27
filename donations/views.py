import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime
from urllib import error as urllib_error
from urllib import request as urllib_request

from django.conf import settings
from django.db.models import Count, Sum
from django.http import StreamingHttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Donation
from .serializers import DonationSerializer


def normalize_status(value):
    current = (value or "").strip().lower()
    if current in {"completed", "complete", "paid", "success", "successful", "succeeded"}:
        return "completed"
    if current in {"failed", "fail", "error", "cancelled", "canceled", "declined"}:
        return "failed"
    return "pending"


def donation_payload(donation):
    return {
        "donation_id": donation.id,
        "payment_status": donation.status,
        "status": donation.status,
        "provider": donation.provider,
        "external_reference": donation.external_reference,
        "gateway_event_id": donation.gateway_event_id,
        "completed_at": donation.completed_at.isoformat() if donation.completed_at else None,
        "failed_reason": donation.failed_reason,
    }


def _normalize_signature(value):
    raw = (value or "").strip()
    for prefix in ("sha256=", "v1="):
        if raw.lower().startswith(prefix):
            return raw[len(prefix) :].strip()
    return raw


def _verify_hmac_hex(secret, payload, provided_signature):
    if not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    provided = _normalize_signature(provided_signature)
    return hmac.compare_digest(expected, provided)


def _bool_setting(name, default=False):
    value = getattr(settings, name, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _sanitize_msisdn(phone):
    digits = "".join(ch for ch in str(phone or "") if ch.isdigit())
    if digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    if digits.startswith("254") and len(digits) == 12:
        return digits
    return ""


def _post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(url, data=data, headers=headers, method="POST")
    with urllib_request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def _mpesa_env():
    use_sandbox = _bool_setting("MPESA_USE_SANDBOX", True)
    base_url = "https://sandbox.safaricom.co.ke" if use_sandbox else "https://api.safaricom.co.ke"
    return {
        "base_url": base_url,
        "consumer_key": (getattr(settings, "MPESA_CONSUMER_KEY", "") or "").strip(),
        "consumer_secret": (getattr(settings, "MPESA_CONSUMER_SECRET", "") or "").strip(),
        "shortcode": (getattr(settings, "MPESA_SHORTCODE", "") or "").strip(),
        "passkey": (getattr(settings, "MPESA_PASSKEY", "") or "").strip(),
        "callback_url": (getattr(settings, "MPESA_CALLBACK_URL", "") or "").strip(),
        "test_phone": _sanitize_msisdn(getattr(settings, "MPESA_TEST_PHONE", "")),
    }


def _trigger_mpesa_stk_push(donation, phone):
    cfg = _mpesa_env()
    missing = [k for k in ("consumer_key", "consumer_secret", "shortcode", "passkey", "callback_url") if not cfg[k]]
    if missing:
        return {
            "requested": False,
            "detail": f"M-Pesa credentials missing: {', '.join(missing)}",
        }

    try:
        auth = base64.b64encode(f"{cfg['consumer_key']}:{cfg['consumer_secret']}".encode("utf-8")).decode("utf-8")
        token_url = f"{cfg['base_url']}/oauth/v1/generate?grant_type=client_credentials"
        token_req = urllib_request.Request(token_url, headers={"Authorization": f"Basic {auth}"}, method="GET")
        with urllib_request.urlopen(token_req, timeout=20) as token_response:
            token_payload = json.loads(token_response.read().decode("utf-8"))
        access_token = token_payload.get("access_token", "")
        if not access_token:
            return {"requested": False, "detail": "Failed to get M-Pesa access token."}

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{cfg['shortcode']}{cfg['passkey']}{timestamp}".encode("utf-8")).decode("utf-8")

        stk_payload = {
            "BusinessShortCode": cfg["shortcode"],
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": max(1, int(float(donation.amount))),
            "PartyA": phone,
            "PartyB": cfg["shortcode"],
            "PhoneNumber": phone,
            "CallBackURL": cfg["callback_url"],
            "AccountReference": donation.external_reference or f"DON-{donation.id}",
            "TransactionDesc": "Donation Payment",
        }
        stk_headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        stk_url = f"{cfg['base_url']}/mpesa/stkpush/v1/processrequest"
        stk_response = _post_json(stk_url, stk_payload, stk_headers)

        checkout_request_id = (stk_response.get("CheckoutRequestID") or "").strip()
        merchant_request_id = (stk_response.get("MerchantRequestID") or "").strip()

        if checkout_request_id:
            donation.external_reference = checkout_request_id
        if merchant_request_id:
            donation.gateway_event_id = merchant_request_id
        donation.provider = "mpesa"
        donation.save(update_fields=["provider", "external_reference", "gateway_event_id"])

        return {
            "requested": True,
            "detail": stk_response.get("CustomerMessage") or stk_response.get("ResponseDescription") or "STK push request sent.",
            "response_code": stk_response.get("ResponseCode"),
            "merchant_request_id": merchant_request_id,
            "checkout_request_id": checkout_request_id,
            "raw": stk_response,
        }
    except urllib_error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="ignore")
        parsed = {}
        try:
            parsed = json.loads(message) if message else {}
        except Exception:
            parsed = {}
        return {
            "requested": False,
            "detail": f"M-Pesa HTTP error: {exc.code}",
            "error": parsed or message or str(exc),
        }
    except Exception as exc:
        return {"requested": False, "detail": f"M-Pesa error: {exc}"}


class BaseWebhookView(APIView):
    permission_classes = [AllowAny]
    provider_name = ""
    secret_setting_name = ""
    signature_header_names = ()

    def _get_secret(self):
        return (getattr(settings, self.secret_setting_name, "") or "").strip()

    def _signature_required(self):
        return _bool_setting("PAYMENT_REQUIRE_WEBHOOK_SIGNATURES", False) or bool(self._get_secret())

    def _extract_signature(self, request):
        for header in self.signature_header_names:
            value = request.headers.get(header)
            if value:
                return value
        return ""

    def verify_signature(self, request):
        secret = self._get_secret()
        required = self._signature_required()

        if not secret:
            return not required

        signature = self._extract_signature(request)
        if not signature:
            return False

        payload = request.body or b""
        return _verify_hmac_hex(secret, payload, signature)

    def post(self, request, *args, **kwargs):
        if not self.verify_signature(request):
            return Response(
                {"detail": f"Invalid {self.provider_name or 'payment'} webhook signature."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data or {}

        donation = None
        donation_id = data.get("donation_id") or data.get("id")
        reference = data.get("external_reference") or data.get("reference")
        gateway_event_id = data.get("gateway_event_id") or data.get("event_id")

        if donation_id:
            donation = Donation.objects.filter(pk=donation_id).first()
        if not donation and reference:
            donation = Donation.objects.filter(external_reference=reference).order_by("-created_at").first()
        if not donation and gateway_event_id:
            donation = Donation.objects.filter(gateway_event_id=gateway_event_id).order_by("-created_at").first()

        if not donation:
            return Response({"detail": "Donation not found for webhook payload."}, status=status.HTTP_404_NOT_FOUND)

        status_value = normalize_status(data.get("status"))
        donation.provider = self.provider_name or donation.provider
        if reference:
            donation.external_reference = str(reference)
        if gateway_event_id:
            donation.gateway_event_id = str(gateway_event_id)

        if status_value == "completed":
            donation.mark_completed()
        elif status_value == "failed":
            reason = (data.get("reason") or data.get("message") or "").strip()
            donation.mark_failed(reason=reason)
        else:
            donation.status = "pending"
            donation.save(update_fields=["status", "provider", "external_reference", "gateway_event_id"])

        donation.refresh_from_db()
        return Response(
            {
                "detail": f"{self.provider_name or 'Payment'} webhook processed.",
                "donation": donation_payload(donation),
            },
            status=status.HTTP_200_OK,
        )


class StripeWebhookView(BaseWebhookView):
    provider_name = "stripe"
    secret_setting_name = "PAYMENT_STRIPE_WEBHOOK_SECRET"
    signature_header_names = ("Stripe-Signature",)

    def verify_signature(self, request):
        secret = self._get_secret()
        required = self._signature_required()

        if not secret:
            return not required

        header_value = request.headers.get("Stripe-Signature", "")
        if not header_value:
            return False

        parts = {}
        for part in header_value.split(","):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            parts.setdefault(key.strip(), []).append(value.strip())

        timestamp_values = parts.get("t", [])
        signatures = parts.get("v1", [])
        if not timestamp_values or not signatures:
            return False

        try:
            timestamp = int(timestamp_values[0])
        except (TypeError, ValueError):
            return False

        tolerance = int(getattr(settings, "PAYMENT_WEBHOOK_TOLERANCE_SECONDS", 300) or 300)
        if abs(int(time.time()) - timestamp) > tolerance:
            return False

        payload = request.body or b""
        signed_payload = f"{timestamp}.".encode("utf-8") + payload
        expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

        return any(hmac.compare_digest(expected, candidate) for candidate in signatures)


class PayPalWebhookView(BaseWebhookView):
    provider_name = "paypal"
    secret_setting_name = "PAYMENT_PAYPAL_WEBHOOK_SECRET"
    signature_header_names = ("Paypal-Transmission-Sig", "X-Paypal-Signature")


class MpesaWebhookView(BaseWebhookView):
    provider_name = "mpesa"
    secret_setting_name = "PAYMENT_MPESA_WEBHOOK_SECRET"
    signature_header_names = ("X-Mpesa-Signature", "X-Webhook-Signature")


class DonationStatusStreamView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk, *args, **kwargs):
        timeout = request.query_params.get("timeout", "60")
        try:
            timeout_seconds = int(timeout)
        except ValueError:
            timeout_seconds = 60
        timeout_seconds = min(max(timeout_seconds, 15), 300)

        def event_stream():
            started_at = time.time()
            last_sent = None

            while time.time() - started_at < timeout_seconds:
                donation = Donation.objects.filter(pk=pk).first()
                if donation is None:
                    payload = {"detail": "Donation not found.", "donation_id": pk}
                    yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                    break

                payload = donation_payload(donation)
                snapshot = json.dumps(payload, sort_keys=True)

                if snapshot != last_sent:
                    yield f"event: status\ndata: {snapshot}\n\n"
                    last_sent = snapshot

                if donation.status in {"completed", "failed"}:
                    break

                yield "event: heartbeat\ndata: {}\n\n"
                time.sleep(2)

            yield "event: end\ndata: {\"closed\": true}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by("-created_at")
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]

    def _status_urls(self, request, donation):
        status_path = f"/api/donations/{donation.id}/payment-status/"
        stream_path = f"/api/donations/{donation.id}/status-stream/"
        return {
            "status_endpoint": request.build_absolute_uri(status_path),
            "stream_endpoint": request.build_absolute_uri(stream_path),
        }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.save(status="pending", external_reference=f"DON-{uuid.uuid4().hex[:12].upper()}")

        out = self.get_serializer(donation)
        urls = self._status_urls(request, donation)
        return Response(
            {
                "detail": "Donation submitted successfully.",
                "payment_status": donation.status,
                "donation": out.data,
                **urls,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="initiate-payment")
    def initiate_payment(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_method = serializer.validated_data.get("payment_method", "mpesa")
        approval_url = None
        mpesa_result = None

        provider = payment_method
        payment_status = "pending"

        donation = serializer.save(
            status=payment_status,
            provider=provider,
            external_reference=f"PAY-{uuid.uuid4().hex[:12].upper()}",
        )

        if payment_method == "paypal":
            approval_url = "https://www.paypal.com"

        if payment_method == "mpesa":
            phone = _sanitize_msisdn(serializer.validated_data.get("phone")) or _mpesa_env()["test_phone"]
            if not phone:
                return Response(
                    {"detail": "M-Pesa phone is required. Provide phone in payload or set MPESA_TEST_PHONE."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            donation.phone = phone
            donation.save(update_fields=["phone"])
            mpesa_result = _trigger_mpesa_stk_push(donation, phone)

        out = self.get_serializer(donation)
        urls = self._status_urls(request, donation)

        response = {
            "detail": "Payment initiated successfully.",
            "payment_status": donation.status,
            "approval_url": approval_url,
            "donation": out.data,
            **urls,
        }
        if mpesa_result is not None:
            response["mpesa"] = mpesa_result

        return Response(response, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="mpesa-check")
    def mpesa_check(self, request):
        cfg = _mpesa_env()
        missing = [k for k in ("consumer_key", "consumer_secret", "shortcode", "passkey", "callback_url") if not cfg[k]]
        callback_ok = cfg["callback_url"].startswith("https://")

        auth_ok = False
        auth_error = ""
        if not missing:
            try:
                auth = base64.b64encode(f"{cfg['consumer_key']}:{cfg['consumer_secret']}".encode("utf-8")).decode("utf-8")
                token_url = f"{cfg['base_url']}/oauth/v1/generate?grant_type=client_credentials"
                token_req = urllib_request.Request(token_url, headers={"Authorization": f"Basic {auth}"}, method="GET")
                with urllib_request.urlopen(token_req, timeout=20) as token_response:
                    token_payload = json.loads(token_response.read().decode("utf-8"))
                auth_ok = bool(token_payload.get("access_token"))
                if not auth_ok:
                    auth_error = "No access token returned from Safaricom."
            except urllib_error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore")
                auth_error = f"HTTP {exc.code}: {body}"
            except Exception as exc:
                auth_error = str(exc)

        return Response(
            {
                "sandbox": cfg["base_url"].startswith("https://sandbox."),
                "base_url": cfg["base_url"],
                "test_phone": cfg["test_phone"],
                "has_consumer_key": bool(cfg["consumer_key"]),
                "has_consumer_secret": bool(cfg["consumer_secret"]),
                "has_shortcode": bool(cfg["shortcode"]),
                "has_passkey": bool(cfg["passkey"]),
                "callback_url": cfg["callback_url"],
                "callback_uses_https": callback_ok,
                "missing": missing,
                "auth_ok": auth_ok,
                "auth_error": auth_error,
                "note": "For real callbacks, use a public HTTPS URL.",
            }
        )

    @action(detail=True, methods=["get"], url_path="payment-status")
    def payment_status(self, request, pk=None):
        donation = self.get_object()
        return Response(donation_payload(donation))

    @action(detail=True, methods=["post"], url_path="update-status", permission_classes=[AllowAny])
    def update_status(self, request, pk=None):
        required_token = (getattr(settings, "PAYMENT_STATUS_UPDATE_TOKEN", "") or "").strip()
        if required_token:
            provided_token = (request.headers.get("X-Payment-Update-Token", "") or "").strip()
            if not hmac.compare_digest(required_token, provided_token):
                return Response({"detail": "Invalid payment update token."}, status=status.HTTP_403_FORBIDDEN)

        donation = self.get_object()
        new_status = normalize_status(request.data.get("status"))
        reason = (request.data.get("reason") or "").strip()

        provider = request.data.get("provider")
        external_reference = request.data.get("external_reference")
        gateway_event_id = request.data.get("gateway_event_id")

        if provider:
            donation.provider = str(provider)
        if external_reference:
            donation.external_reference = str(external_reference)
        if gateway_event_id:
            donation.gateway_event_id = str(gateway_event_id)

        if new_status == "completed":
            donation.mark_completed()
        elif new_status == "failed":
            donation.mark_failed(reason)
        else:
            donation.status = "pending"
            donation.save(update_fields=["status", "provider", "external_reference", "gateway_event_id"])

        donation.refresh_from_db()
        return Response({"detail": "Payment status updated.", **donation_payload(donation)})

    @action(detail=False, methods=["get"], url_path="payment-section")
    def payment_section(self, request):
        return Response(
            {
                "title": "Secure and flexible payment options",
                "copy": "Choose your preferred payment method. Donations are first recorded as pending for verification.",
                "supported_currencies": ["USD", "KES", "EUR", "GBP"],
                "methods": [
                    {"id": "visa", "label": "Visa", "backend_value": "card", "requires_token": True, "enabled": True},
                    {"id": "paypal", "label": "PayPal", "backend_value": "paypal", "requires_token": True, "enabled": True},
                    {"id": "mpesa", "label": "M-Pesa", "backend_value": "mpesa", "requires_token": True, "enabled": True},
                    {"id": "bank", "label": "Bank", "backend_value": "bank", "requires_token": True, "enabled": True},
                ],
                "submit_endpoint": "/api/donations/",
                "initiate_endpoint": "/api/donations/initiate-payment/",
                "realtime": {
                    "transport": "SSE",
                    "stream_endpoint_template": "/api/donations/{id}/status-stream/",
                    "status_endpoint_template": "/api/donations/{id}/payment-status/",
                },
                "webhook_security": {
                    "stripe_header": "Stripe-Signature",
                    "paypal_headers": ["Paypal-Transmission-Sig", "X-Paypal-Signature"],
                    "mpesa_headers": ["X-Mpesa-Signature", "X-Webhook-Signature"],
                },
                "mpesa": {
                    "test_phone": _mpesa_env()["test_phone"],
                    "uses_real_stk_push_when_credentials_present": True,
                    "check_endpoint": "/api/donations/mpesa-check/",
                },
            }
        )

    @action(detail=False, methods=["get"], url_path="payment-stats")
    def payment_stats(self, request):
        aggregate = Donation.objects.filter(status="completed").aggregate(total_amount=Sum("amount"))
        by_method = (
            Donation.objects.filter(status="completed")
            .values("payment_method")
            .annotate(count=Count("id"))
            .order_by("payment_method")
        )
        return Response(
            {
                "total_amount": aggregate["total_amount"] or 0,
                "total_donations": Donation.objects.filter(status="completed").count(),
                "by_method": list(by_method),
            }
        )

    @action(detail=False, methods=["get"])
    def total(self, request):
        total_amount = Donation.objects.filter(status="completed").aggregate(Sum("amount"))["amount__sum"] or 0
        total_donations = Donation.objects.filter(status="completed").count()
        return Response({"total_amount": total_amount, "total_donations": total_donations})
