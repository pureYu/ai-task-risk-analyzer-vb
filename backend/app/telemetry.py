"""OpenTelemetry (APM) setup.

Configures a tracer provider with a console exporter by default. If the
environment variable `OTEL_EXPORTER_OTLP_ENDPOINT` is set (e.g. a Jaeger or
collector endpoint), an OTLP exporter is added as well.
"""
from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

_SERVICE_NAME = "ai-task-risk-analyzer"
_configured = False


def setup_telemetry() -> TracerProvider:
    """Initialize the global tracer provider once and return it.

    Always emits spans to the console. Adds an OTLP exporter when
    `OTEL_EXPORTER_OTLP_ENDPOINT` is configured.
    """
    global _configured

    provider = trace.get_tracer_provider()
    if _configured and isinstance(provider, TracerProvider):
        return provider

    resource = Resource.create({"service.name": _SERVICE_NAME})
    provider = TracerProvider(resource=resource)

    # Console exporter — zero-infra APM, visible in the server logs.
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    # Optional OTLP exporter (Jaeger / OpenTelemetry Collector).
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
        )

    trace.set_tracer_provider(provider)
    _configured = True
    return provider
