from peewee import BooleanField, FloatField, ForeignKeyField, IntegerField, TextField
from playhouse.shortcuts import model_to_dict
from playhouse.sqlite_ext import JSONField

from .base import BaseModel
from .campaign import Layer
from .user import User
from .utils import get_table


__all__ = [
    "AssetRect",
    "Aura",
    "Circle",
    "CircularToken",
    "Line",
    "MultiLine",
    "Polygon",
    "Rect",
    "Shape",
    "ShapeOwner",
    "Text",
    "Tracker",
]


class Shape(BaseModel):
    uuid = TextField(primary_key=True)
    layer = ForeignKeyField(Layer, backref="shapes", on_delete="CASCADE")
    type_ = TextField()
    x = FloatField()
    y = FloatField()
    name = TextField(null=True)
    name_visible = BooleanField(default=True)
    fill_colour = TextField(default="#000")
    stroke_colour = TextField(default="#fff")
    vision_obstruction = BooleanField(default=False)
    movement_obstruction = BooleanField(default=False)
    is_token = BooleanField(default=False)
    annotation = TextField(default="")
    draw_operator = TextField(default="source-over")
    index = IntegerField()
    options = TextField(null=True)

    def __repr__(self):
        return f"<Shape {self.get_path()}>"

    def get_path(self):
        return f"{self.name}@{self.layer.get_path()}"

    def as_dict(self, user: User, dm: bool):
        data = model_to_dict(self, recurse=False, exclude=[Shape.layer, Shape.index])
        # Owner query > list of usernames
        data["owners"] = [
            so.user.name for so in self.owners.select(User.name).join(User)
        ]
        # Layer query > layer name
        data["layer"] = self.layer.name
        # Aura and Tracker queries > json
        owned = dm or (user.name in data["owners"])
        tracker_query = self.trackers
        aura_query = self.auras
        if not owned:
            data["annotation"] = ""
            tracker_query = tracker_query.where(Tracker.visible)
            aura_query = aura_query.where(Aura.visible)
        if not self.name_visible:
            data["name"] = "?"
        data["trackers"] = [t.as_dict() for t in tracker_query]
        data["auras"] = [a.as_dict() for a in aura_query]
        # Subtype
        type_table = get_table(self.type_)
        data.update(
            **model_to_dict(type_table.get(uuid=self.uuid), exclude=[type_table.uuid])
        )

        return data


class Tracker(BaseModel):
    uuid = TextField(primary_key=True)
    shape = ForeignKeyField(Shape, backref="trackers", on_delete="CASCADE")
    visible = BooleanField()
    name = TextField()
    value = IntegerField()
    maxvalue = IntegerField()

    def __repr__(self):
        return f"<Tracker {self.name} {self.shape.get_path()}>"

    def as_dict(self):
        return model_to_dict(self, recurse=False, exclude=[Tracker.shape])


class Aura(BaseModel):
    uuid = TextField(primary_key=True)
    shape = ForeignKeyField(Shape, backref="auras", on_delete="CASCADE")
    vision_source = BooleanField()
    visible = BooleanField()
    name = TextField()
    value = IntegerField()
    dim = IntegerField()
    colour = TextField()

    def __repr__(self):
        return f"<Aura {self.name} {self.shape.get_path()}>"

    def as_dict(self):
        return model_to_dict(self, recurse=False, exclude=[Aura.shape])


class ShapeOwner(BaseModel):
    shape = ForeignKeyField(Shape, backref="owners", on_delete="CASCADE")
    user = ForeignKeyField(User, backref="shapes", on_delete="CASCADE")

    def __repr__(self):
        return f"<ShapeOwner {self.user.name} {self.shape.get_path()}>"


class ShapeType(BaseModel):
    abstract = True
    uuid = TextField(primary_key=True)


class BaseRect(ShapeType):
    abstract = True
    width = FloatField()
    height = FloatField()


class AssetRect(BaseRect):
    abstract = False
    src = TextField()


class Circle(ShapeType):
    abstract = False
    radius = FloatField()


class CircularToken(Circle):
    abstract = False
    text = TextField()
    font = TextField()


class Line(ShapeType):
    abstract = False
    x2 = FloatField()
    y2 = FloatField()
    line_width = IntegerField()


class MultiLine(ShapeType):
    abstract = False
    line_width = IntegerField()
    points = JSONField()


class Polygon(ShapeType):
    abstract = False
    vertices = JSONField()


class Rect(BaseRect):
    abstract = False


class Text(ShapeType):
    abstract = False
    text = TextField()
    font = TextField()
    angle = FloatField()
