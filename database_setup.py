#!/usr/bin/env python3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date
from sqlalchemy.orm import relationship

Base = declarative_base()


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    instructions = Column(Text)
    created_date = Column(Date)
    category_id = Column(Integer, ForeignKey('category.id'))
    author = Column(Text)

    category = relationship("Category", back_populates="recipes")


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String)
    author = Column(Text)

    recipes = relationship("Recipe", back_populates="category")
