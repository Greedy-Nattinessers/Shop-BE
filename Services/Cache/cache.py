from aiocache import Cache
from aiocache.serializers import JsonSerializer

cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
