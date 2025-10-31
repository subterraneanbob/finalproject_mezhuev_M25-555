class SingletonMeta(type):
    """
    Метакласс для создания классов, которые могут иметь только один экземпляр.
    Реализация через метакласс удобна из-за простоты: класс описывается
    как обычно, нужно только указать metaclass в определении.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Создаёт только один экземпляр класса, который использует этот метакласс
        в определении.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
