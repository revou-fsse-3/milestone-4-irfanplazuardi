from models.base import Base
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import mapped_column, relationship, backref
from sqlalchemy.sql import func
from datetime import datetime
import bcrypt
from flask_login import UserMixin

class User(Base, UserMixin):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(255), nullable= False, unique=True)
    email = mapped_column(String(255), nullable= False, unique=True)
    password = mapped_column(String(255), nullable= True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=datetime.now)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def set_password(self, password):
        self.password = bcrypt.hashpw( password.encode('utf-8') , bcrypt.gensalt()).decode('utf-8') 

    def check_password(self, password):
        return bcrypt.checkpw( password.encode('utf-8') , self.password.encode('utf-8') )