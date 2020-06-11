from flask_restful import Resource, reqparse
from connector.redisgraph import query_redisgraph
from routes.utils import addargs, makeResponse

parser = reqparse.RequestParser()


class CountAllAnnotations(Resource):
    def get(self):
        req = "MATCH (:annotation) RETURN count(*) AS nb_annotations"
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_annotations'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountAnnotationsOnPosts(Resource):
      def get(self):
        req = "MATCH (a:annotation)-[:ANNOTATES]->(:post) RETURN count(a) AS nb_annotations"
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_annotations'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountAnnotationsByPost(Resource):
    def get(self, post_id):
        req = "MATCH (a:annotation)-[:ANNOTATES]->(:post {post_id: %d}) RETURN count(a) AS nb_annotations" % post_id
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_annotations'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountAnnotationsOnComments(Resource):
    def get(self):
        req = "MATCH (a:annotation)-[:ANNOTATES]->(:comment) RETURN count(a) AS nb_annotations"
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_annotations'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountAnnotationsByComment(Resource):
    def get(self, comment_id):
        req = "MATCH (a:annotation)-[:ANNOTATES]->(:comment {comment_id: %d}) RETURN count(a) AS nb_annotations" % comment_id
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_annotations'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountAnnotationsByAuthor(Resource):
    def get(self, user_id):
        req = "MATCH (a:annotation)<-[:AUTHORSHIP]-(:user {user_id: %d}) RETURN count(a) AS nb_annotations" % user_id
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_annotations'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)
