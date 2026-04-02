from fastapi import APIRouter

router = APIRouter(tags=['health'])


@router.get('/health/live')
def live() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/health/ready')
def ready() -> dict[str, str]:
    return {'status': 'ready'}
