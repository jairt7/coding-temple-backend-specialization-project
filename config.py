
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/mechanic_db'
    DEBUG = True

class TestingConfig:
    pass

class ProductionConfig:
    pass
