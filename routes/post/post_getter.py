from flask_restful import Resource
from connector.redisgraph import query_redisgraph
from routes.utils import addargs, makeResponse
import datetime

class GetPost(Resource):
    def get(self, post_id):
        req = "MATCH (find:post {id: %d}) RETURN find" % post_id
        result = query_redisgraph(req)
        try:
            return makeResponse(result['find'].properties, 200)
        except ResultError:
            return makeResponse("ERROR : Cannot find post with cid: %d" % post_id, 204)


class GetPostHydrate(Resource):
    def get(self, post_id):
        req = "MATCH (find:post {id: %d}) " % post_id
        req += "OPTIONAL MATCH (find)<-[:AUTHORSHIP]-(author:user) "
        req += "OPTIONAL MATCH (find)-[:COMMENTS]->(post:post) "
        req += "RETURN find, author.user_id AS user_id, author.label AS user_name, post.id AS post_id, post.title AS post_title, post.url AS post_url"
        result = query_redisgraph(req)
        author = {}
        post = {}
        for record in result:
            post = record['find'].properties
            try:
                if record['user_id']:
                    author['user_id'] = record['user_id']
                if record['user_name']:
                    author['user_name'] = record['user_name']
                if record['post_id']:
                    post['post_id'] = record['post_id']
                if record['post_title']:
                    post['post_title'] = record['post_title']
                if record['post_url']:
                    post['post_url'] = record['post_url']
            except KeyError:
                pass
        # annotations
        req = "MATCH (find:post {id: %d}) " % post_id
        req += "OPTIONAL MATCH (find)<-[:ANNOTATES]-(a:annotation) "
        req += "OPTIONAL MATCH (a)-[:REFERS_TO]->(t:tag) "
        req += "RETURN a.annotation_id as annotation_id, a.timestamp as annotation_timestamp, t.tag_id as tag_id, t.label as tag_label"
        result = query_redisgraph(req)
        annotations = []
        annotations_id = []
        for record in result:
            annotation = {}
            try:
                if record['tag_id'] and record['annotation_id'] not in annotations_id:
                    if record['annotation_id']:
                        annotation['annotation_id'] = record['annotation_id']
                    if record['annotation_timestamp']:
                        annotation['annotation_timestamp'] = record['annotation_timestamp']
                    if record['tag_id']:
                        annotation['tag_id'] = record['tag_id']
                    if record['tag_label']:
                        annotation['tag_label'] = record['tag_label']
                    annotations.append(annotation)
                    annotations_id.append(record['annotation_id'])
            except KeyError:
                pass

        # response posts
        req = 'MATCH (find:post {id: %d}) ' % post_id
        req += 'OPTIONAL MATCH (find)<-[:COMMENTS]-(c2:post) '
        req += 'OPTIONAL MATCH (c2:post)<-[:AUTHORSHIP]-(author:user) '
        req += 'RETURN find.id AS initial_post_id, c2.post_id AS response_id, c2.label AS response_label, c2.timestamp AS response_timestamp, author.user_id AS author_id, author.label AS author_label ORDER BY response_timestamp DESC'
        result = query_redisgraph(req)
        resp_posts = []
        for record in result:
            resp_post = {}
            try:
                if record['response_id']:
                    resp_post['post_id'] = record['response_id']
                    if record['response_label']:
                        resp_post['post_label'] = record['response_label']
                    if record['response_timestamp']:
                        resp_post['post_timestamp'] = record['response_timestamp']
                    if record['author_id']:
                        resp_post['user_id'] = record['author_id']
                    if record['author_label']:
                        resp_post['user_label'] = record['author_label']
                    resp_posts.append(resp_post)
            except KeyError:
                pass

        try:
            post
        except NameError:
            return "ERROR : Cannot find post with pid: %d" % post_id, 200
        post['author'] = author
        post['post'] = post
        post['annotations'] = annotations
        post['posts'] = resp_posts
        return makeResponse(post, 200)


class GetPosts(Resource):
    def get(self):
        req = "MATCH (c:post)<-[:AUTHORSHIP]-(u:user) MATCH (c)-[:COMMENTS]->(p:post) RETURN c.id AS post_id, c.title AS title, c.content AS content, c.timestamp AS timestamp, u.user_id AS user_id"
        req += addargs()
        result = query_redisgraph(req)
        posts = []
        for record in result:
            fmt_time = datetime.datetime.fromtimestamp(record['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
            posts.append({'post_id': record['post_id'], "title": record['title'], "content": record["content"], "date": fmt_time, "user_id": record["user_id"], "post_id": record["post_id"]})
        return makeResponse(posts, 200)


class GetPostsLatest(Resource):
    def get(self):
        req = "MATCH (c: post) <-[:AUTHORSHIP]- (u: user) RETURN c.id AS post_id, c.label AS post_label, u.user_id AS user_id, u.label AS user_label, c.timestamp AS timestamp ORDER BY timestamp DESC LIMIT 5"
        result = query_redisgraph(req)
        posts = []
        for record in result:
            posts.append({'post_id': record['post_id'], "post_label": record['post_label'], "user_id": record['user_id'], "user_label": record['user_label'], "timestamp": record['timestamp']})
        return makeResponse(posts, 200)


class GetPostsByAuthor(Resource):
    def get(self, author_id):
        req = "MATCH (author:user {id: %d})-[:AUTHORSHIP]->(c:post) RETURN c" % author_id
        req += addargs()
        result = query_redisgraph(req)
        posts = []
        for record in result:
            posts.append(record['c'].properties)
        return makeResponse(posts, 200)


class GetPostsOnPost(Resource):
    def get(self, post_id):
        req = "MATCH (c:post)-[:COMMENTS]->(post:post {id: %d}) RETURN c" % post_id
        req += addargs()
        result = query_redisgraph(req)
        posts = []
        for record in result:
            posts.append(record['c'].properties)
        return makeResponse(posts, 200)


class GetPostsOnPost(Resource):
    def get(self, post_id):
        req = "MATCH (c:post)-[:COMMENTS]->(post:post {id: %d}) RETURN c" % post_id
        req += addargs()
        result = query_redisgraph(req)
        posts = []
        for record in result:
            posts.append(record['c'].properties)
        return makeResponse(posts, 200)
