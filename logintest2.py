import re
from mechanize import Browser

br = Browser()
br.open("http://www.proxyfire.net/forum/login.php")
# follow second link with element text matching regular expression

assert br.viewing_html()
print br.title()
print br.geturl()
#print br.info()  # headers
#print br.read()  # body
#br.close()  # (shown for clarity; in fact Browser does this for you)

br.select_form(name="vb_login_username=User Name")
# Browser passes through unknown attributes (including methods)
# to the selected HTMLForm (from ClientForm).
br["vb_login_username"] = ["sleven"]  # (the method here is __setitem__)
response2 = br.submit()  # submit current form

# print currently selected form (don't call .submit() on this, use br.submit())
print br.form

response3 = br.back()  # back to cheese shop (same data as response1)
# the history mechanism returns cached response objects
# we can still use the response, even though we closed it:
response3.seek(0)
response3.read()
response4 = br.reload()  # fetches from server

for form in br.forms():
    print form
# .links() optionally accepts the keyword args of .follow_/.find_link()
for link in br.links(url_regex="python.org"):
    print link
    br.follow_link(link)  # takes EITHER Link instance OR keyword args
    br.back()
