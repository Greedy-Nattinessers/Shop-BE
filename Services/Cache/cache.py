from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer

cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
