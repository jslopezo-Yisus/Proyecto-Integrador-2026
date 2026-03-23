class Config:
    SECRET_KEY = "clave_super_secreta"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456789@localhost/proyecto_viviendas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False