from fastapi import APIRouter,Request
router = APIRouter()

@router.get("/another-example/another-new-endpoint")
async def another_test():
    return "Another Thing"