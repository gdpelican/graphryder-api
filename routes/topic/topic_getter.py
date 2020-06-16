from flask_restful import Resource, reqparse
from connector.redisgraph import query_redisgraph
from routes.utils import addargs, addTimeFilter, makeResponse
import datetime

parser = reqparse.RequestParser()

class GetPost(Resource):
    def get(self, topic_id):
        result = query_redisgraph("MATCH (find:topic {topic_id: %d}) RETURN find" % topic_id)
        try:
            return makeResponse(result.single()['find'].properties, 200)
        except ResultError:
            return makeResponse("ERROR : Cannot find topic with pid: %d" % topic_id, 204)


class GetPostHydrate(Resource): # todo posts on posts (with author)
    def get(self, topic_id):
        req = "MATCH (find:topic {id: %d}) " % topic_id
        req += "OPTIONAL MATCH (find)<-[:AUTHORSHIP]-(author:user) "
        req += "OPTIONAL MATCH (find)<-[:COMMENTS]-(post:post) "
        req += "OPTIONAL MATCH (post)<-[:AUTHORSHIP]-(postAuthor:user) "
        req += "RETURN find, author, post, postAuthor ORDER BY post.timestamp DESC"
        result = query_redisgraph(req)
        posts = []
        author = None
        for record in result:
            topic = record['find'].properties
            try:
                if record['author']:
                    author = record['author'].properties
                if record['post']:
                    post = record['post'].properties
                    if record['postAuthor']:
                        post['author'] = record['postAuthor'].properties
                    posts.append(post)
            except KeyError:
                pass

        # annotations
        req = "MATCH (find:topic {topic_id: %d}) " % topic_id
        req += "OPTIONAL MATCH (find)<-[:ANNOTATES]-(a:annotation) "
        req += "OPTIONAL MATCH (a)-[:REFERS_TO]->(t:tag) "
        req += "RETURN a.annotation_id as annotation_id, a.timestamp as annotation_timestamp, t.tag_id as tag_id, t.label as tag_label ORDER BY a.timestamp DESC"
        result = query_redisgraph(req)
        annotations = []
        annotations_id = []
        tags_id = []
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
                    if record['tag_id'] not in tags_id:
                        tags_id.append(record['tag_id'])
            except KeyError:
                pass

        # innovations
        req = "MATCH (p: topic {topic_id: %d}) <-[:COMMENTS]- (c: post) " %topic_id
        req += "MATCH (c) <-[:ANNOTATES]-(a)-[:REFERS_TO]->(t: tag) "
        req += "RETURN t.tag_id as tag_id, t.label as tag_label, c.post_id as post_id, c.label as post_label ORDER BY c.timestamp DESC"
        result = query_redisgraph(req)
        innovations = []
        for record in result:
            innovation = {}
            try:
                if record['tag_id'] and record['tag_id'] not in tags_id:
                    if record['tag_id']:
                        innovation['tag_id'] = record['tag_id']
                    if record['tag_label']:
                        innovation['tag_label'] = record['tag_label']
                    if record['post_id']:
                        innovation['post_id'] = record['post_id']
                    if record['post_label']:
                        innovation['post_label'] = record['post_label']
                    innovations.append(innovation)
            except KeyError:
                pass

        try:
            topic
        except NameError:
            return "ERROR : Cannot find topic with pid: %d" % topic_id, 200
        topic['posts'] = posts
        topic['author'] = author
        topic['annotations'] = annotations
        topic['innovations'] = innovations
        return makeResponse(topic, 200)


class GetPosts(Resource):
    def get(self):
        req = "MATCH (p:topic)<-[:AUTHORSHIP]-(u:user) RETURN p.topic_id AS topic_id, p.title AS title, p.content AS content, p.timestamp AS timestamp, u.user_id AS user_id"
        req += addargs()
        result = query_redisgraph(req)
        topics = []
        for record in result:
            fmt_time = datetime.datetime.fromtimestamp(record['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
            topics.append({'topic_id': record['topic_id'], "title": record['title'], "content": record["content"], "timestamp": fmt_time, "user_id": record["user_id"]})
        return makeResponse(topics, 200)

class GetPostsLatest(Resource):
    def get(self):
        req = "MATCH (p:topic) <-[:AUTHORSHIP]- (u: user) RETURN p.topic_id AS topic_id,p.label AS topic_label, u.user_id AS user_id, u.label AS user_label, p.timestamp AS timestamp ORDER BY timestamp DESC LIMIT 5"
        result = query_redisgraph(req)
        topics = []
        for record in result:
            topics.append({'topic_id': record['topic_id'], "topic_label": record['topic_label'], "user_id": record['user_id'], "user_label": record['user_label'], "timestamp": record['timestamp']})
        return makeResponse(topics, 200)


class GetPostsByType(Resource):
    def get(self, topic_type):
        req = "MATCH (find:topic {type: '%s'}) RETURN find" % topic_type
        req += addargs()
        result = query_redisgraph(req)
        topics = []
        for record in result:
            topics.append(record['find'].properties)
        return makeResponse(topics, 200)


class GetPostsByAuthor(Resource):
    def get(self, author_id):
        req = "MATCH (author:user {user_id: %d})-[:AUTHORSHIP]->(p:topic) RETURN p" % author_id
        req += addargs()
        result = query_redisgraph(req)
        topics = []
        for record in result:
            topics.append(record['p'].properties)
        return makeResponse(topics, 200)


class GetPostType(Resource):
    def get(self):
        parser.add_argument('uid', action='append')
        args = parser.parse_args()

        if args['uid']:
            req = "MATCH (n:topic_type)<-[r:TYPE_IS]-(p:topic) "
            req += addTimeFilter()
            for user in args['uid']:
                req += "OPTIONAL MATCH (n)<-[r%s:TYPE_IS]-(p:topic)<-[]-(u%s:user {uid: %s}) " % (user, user, user)
            req += "RETURN n, count(r) AS nb_topics"
            for user in args['uid']:
                req += ", count(r%s) AS u%s_topics" % (user, user)
        else:
            req = "MATCH (n:topic_type)<-[r:TYPE_IS]-(p:topic) "
            req += addTimeFilter()
            req += "RETURN n, count(r) AS nb_topics"
        result = query_redisgraph(req)
        labels = []
        data = [[]]
        if args['uid']:
            for user in args['uid']:
                data.append([])
        for record in result:
            labels.append(record['n'].properties['name'])
            data[0].append(record['nb_topics'])
            if args['uid']:
                count = 1
                for user in args['uid']:
                    data[count].append(record['u%s_topics' % user])
                    count += 1
        return makeResponse({'labels': labels, 'data': data}, 200)
