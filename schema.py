import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from database import db_session, User as UserModel
from sqlalchemy import and_


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    def mutate(self, info, email):
        user = UserModel(email=email)
        db_session.add(user)
        db_session.commit()
        ok = True
        return CreateUser(user=user, ok=ok)


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return 'Hello ' + name


class MyMutations(graphene.ObjectType):
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=MyMutations)