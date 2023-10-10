class Entity:
    def __call__(self, cls):
        print(self)
        print(cls)
        return cls

@Entity()
class User:
    pass

s = User()
