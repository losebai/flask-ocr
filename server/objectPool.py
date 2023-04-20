

class ObjectPool:
    def __init__(self, object_factory:any, max_objects):
        self.object_factory = object_factory
        self.max_objects = max_objects
        self.available_objects = [self.object_factory() for i in range(max_objects)]
        self.used_objects = []

    def acquire(self)->any:
        if self.available_objects:
            obj = self.available_objects.pop()
        elif len(self.used_objects) < self.max_objects:
            obj = self.object_factory()
        else:
            raise Exception("Object pool exhausted")
        self.used_objects.append(obj)
        return obj

    def release(self, obj):
        if obj in self.used_objects:
            self.used_objects.remove(obj)
            self.available_objects.append(obj)

    def size(self):
        return len(self.available_objects)
