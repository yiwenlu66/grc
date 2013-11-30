# -*- coding: utf-8 -*-
import webapp2
import jinja2
import os
import random
import time
import itertools
import logging
from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

jinja_env.globals['len'] = len
jinja_env.globals['str'] = str


def render_str(template, autoescape=True, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Group(db.Model):
    name_en = db.StringProperty(required=True)
    name_ch = db.StringProperty(required=True)
    enabled = db.BooleanProperty(required=True)


class Question(db.Model):
    q_class = db.IntegerProperty(required=True)
    # Currently Supported:
    #    0 - Random Blanks
    #    1 - Strict Blanks
    group = db.StringProperty(required=True)
    # Group name (in English), correspondent with the groups dictionary
    title = db.StringProperty(default=" ")
    question = db.TextProperty(required=True)
    answer = db.StringListProperty()
    # Not required for q_class 0 (in which answer is from the question)
    created = db.DateTimeProperty(auto_now_add=True)
    # Used for ordered revision


class Visitor(db.Model):
    user_id = db.IntegerProperty(required=True)
    visit_time = db.DateTimeProperty(auto_now_add=True)
    ip = db.StringProperty()
    groups = db.StringListProperty(required=True)
    order = db.IntegerProperty(required=True)
    # 0 for random, 1 for ordered
    feedback = db.TextProperty()
    contact = db.TextProperty()


class BaseHandler(webapp2.RequestHandler):

    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def redirect(self, url):
        if self.request.remote_addr == "74.117.59.181":
            webapp2.RequestHandler.redirect(
                self, "http://shs1509-grc.appsp0t.com" + url)
        else:
            webapp2.RequestHandler.redirect(self, url)


class Portal(BaseHandler):

    def init_groups(self):
        if not len(list(db.GqlQuery("select * from Group"))):
            group = Group(name_en="test", name_ch="test", enabled=False)
            group.put()
        # Init a Group instance
        if not len(list(db.GqlQuery("select * from Question"))):
            question = Question(group="test", q_class=0, question="test")
            question.put()
        # Init a Question instance
        groups = memcache.get("groups")
        if not groups:
            groups = list(db.GqlQuery(
                "select * from Group where enabled=True"))
            memcache.set("groups", groups)
        self.groups_en_ch = [(item.name_en, item.name_ch) for item in groups]
        # Read enabled groups from memcache or DB

    def get(self):
        self.init_groups()
        self.render("portal.html", ip_warning=(self.request.remote_addr == "74.117.59.181"), groups=[item[1]
                                                                                                     for item in self.groups_en_ch])
        # Render Chinese names

    def post(self):
        try:
            self.init_groups()
            groups_selected = []
            for i in range(len(self.groups_en_ch)):
                if self.request.get("group%d" % i):
                    groups_selected.append(self.groups_en_ch[i][0])
            # Get selected groups
            order = eval(self.request.get("order"))
            # Get selected order (0 for random, 1 for ordered)
            user_id = self.request.cookies.get("user_id")
            if not user_id:
                user_id = str(random.randint(0, 10000000))
                expires = time.strftime("%a, %d-%b-%Y %T GMT",
                                        time.gmtime(time.time() + 300 * 24 * 3600))
                self.response.headers.add_header(
                    "Set-cookie", "user_id=%s; Path=/; Expires=%s" % (user_id, expires))
            # Generate a user_id if not found in cookies
            self.response.headers.add_header(
                "Set-cookie", "groups=%s; Path=/" % (str(groups_selected)[1:-1]).replace(", ", "|"))
            self.response.headers.add_header(
                "Set-cookie", "order=%d; Path=/" % order)
            if order:
                self.response.headers.add_header(
                    "Set-cookie", "gseq=0; Path=/")
                # Group Sequence
                self.response.headers.add_header(
                    "Set-cookie", "qseq=0; Path=/")
                # Question Sequence
            # Record current gseq & qseq for ordered revision
            else:
                self.response.headers.add_header(
                    "Set-cookie", "chosen=set(); Path=/")
                self.response.headers.add_header("Set-cookie", "gseq=; Path=/")
                self.response.headers.add_header("Set-cookie", "qseq=; Path=/")
            # Record chosen (group, question) tuples for random revision
            self.redirect("/review")
            visitor_session = Visitor(
                user_id=int(user_id), ip=self.request.remote_addr, groups=groups_selected, order=order)
            visitor_session.put()
        except:
            self.redirect("/")


class Review(BaseHandler):

    def get_questions(self, name_en):
        """Given the English name of the group
        Return a list of questions from memcache or DB"""
        questions = memcache.get(name_en)
        if not questions:
            questions = list(
                db.GqlQuery("select * from Question where group=:1 order by created asc", name_en))
            memcache.set(name_en, questions)
        return questions

    def finish(self):
        """Clear cookies and render the finish page"""
        self.response.headers.add_header("Set-cookie", "groups=; Path=/")
        self.response.headers.add_header("Set-cookie", "order=; Path=/")
        self.response.headers.add_header("Set-cookie", "gseq=; Path=/")
        self.response.headers.add_header("Set-cookie", "qseq=; Path=/")
        self.response.headers.add_header("Set-cookie", "chosen=; Path=/")
        self.render("finish.html", ip_warning=(
            self.request.remote_addr == "74.117.59.181"))

    def get(self):
        try:
            groups = eval(
                ("[" + self.request.cookies.get("groups") + "]").replace("|", ","))
            order = eval(self.request.cookies.get("order"))
            if order:
                gseq = eval(self.request.cookies.get("gseq"))
                qseq = eval(self.request.cookies.get("qseq"))
                questions = self.get_questions(groups[gseq])
                if qseq == len(questions):
                    gseq += 1
                    qseq = 0
                    self.response.headers.add_header("Set-cookie", "gseq=%s; Path=/"%gseq)
                    self.response.headers.add_header("Set-cookie", "qseq=%s; Path=/"%qseq)
                # Advance to next group
                if gseq == len(groups):
                    self.finish()
                    return
                self.render("review.html", ip_warning=(
                    self.request.remote_addr == "74.117.59.181"), question=questions[qseq])
            else:
                all_questions = list(itertools.chain(
                    *[self.get_questions(group) for group in groups]))
                chosen = eval(
                    self.request.cookies.get("chosen").replace("|", ","))
                if len(chosen) == len(all_questions):
                    self.finish()
                    return
                qseq_to_render = random.choice(
                    list(set(range(len(all_questions))) - chosen))
                self.render(
                    "review.html", ip_warning=(self.request.remote_addr == "74.117.59.181"),
                    question=all_questions[qseq_to_render])
                chosen.add(qseq_to_render)
                self.response.headers.add_header(
                    "Set-cookie", "chosen=%s; Path=/" % ("{" + str(chosen)[5:-2] + "}").replace(", ", "|"))
                # Avoid cookies with [] ,space or ','
        except:
            self.redirect("/")


class About(BaseHandler):

    def get(self):
        self.render("about.html", ip_warning=(
            self.request.remote_addr == "74.117.59.181"))


class Feedback(BaseHandler):

    def get(self):
        self.render("feedback.html", ip_warning=(
            self.request.remote_addr == "74.117.59.181"))

    def post(self):
        feedback = self.request.get("feedback")
        contact = self.request.get("contact")
        user_id = int(self.request.cookies.get("user_id"))
        user_query = db.GqlQuery(
            "select * from Visitor where user_id=:1", user_id)
        this_user = list(user_query)[0]
        this_user.feedback = feedback
        this_user.contact = contact
        this_user.put()
        self.redirect("/")

from add_data import AddData

app = webapp2.WSGIApplication([
    ('/', Portal),
    ('/review', Review),
    ('/about', About),
    ('/feedback', Feedback),
    ('/add_data', AddData)
], debug=True)
