from django.core.cache import cache

def cache_decorator(key, expiry=60*60):
    def _cache_decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = key
            if len(args) > 0:
                cache_key += "-".join(str(el) for el in args)

            if len(kwargs) > 0:
                cache_key += "-".join(f"{k}-{v}" for k, v in kwargs.items())

            cached_obj = cache.get(cache_key)
            if cached_obj is not None:
                print(f"Cache hit: {cache_key}")
                return cached_obj
            print(f"Cache miss: {cache_key}")


            obj = func(*args, **kwargs)
            cache.set(cache_key, obj, expiry)
            return obj
        return wrapper
    return _cache_decorator

