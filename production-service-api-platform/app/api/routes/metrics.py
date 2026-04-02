from fastapi import APIRouter, Response
from app.services.metrics import client_counter, endpoint_errors, render_metrics

router = APIRouter(tags=['metrics'])


@router.get('/metrics')
def metrics() -> Response:
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)


@router.get('/internal/usage-summary')
def usage_summary() -> dict:
    return {
        'client_request_counts': dict(client_counter),
        'endpoint_errors': {f'{path}:{status}': count for (path, status), count in endpoint_errors.items()},
    }
