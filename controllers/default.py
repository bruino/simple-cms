# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

def index():
    """List pages"""
    pages = db().select(db.page_cms.id, db.page_cms.title, orderby=~db.page_cms.id)
    return dict(pages=pages)

def show():
    """Show a page"""
    page = db.page_cms[request.args(0, cast=int)] or redirect(URL('index'))
    response.title = page.title
    return dict(page=page)

@auth.requires_login()
def create():
    """Create page"""
    form = SQLFORM(db.page_cms).process(next=URL('index'))
    return dict(form=form)

@auth.requires_login()
def edit():
    """Edit an existing page"""
    page = db.page_cms[request.args(0, cast=int)] or redirect(URL('index'))
    form = SQLFORM(db.page_cms, page).process(next=URL('show',args=request.args))
    return dict(form=form)

@auth.requires_signature()
def save():
    """POST. Save page"""
    body = request.post_vars.body
    page_id = request.post_vars.page_id
    id = db(db.page_cms.id == int(page_id)).update(body=body) if not None in (body, page_id) else None
    return HTTP(200) if id else HTTP(403)

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)