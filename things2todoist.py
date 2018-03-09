#!/usr/local/bin/python3

# `pip3 install todoist-python`
#
# Usage: ./things2todoist.py input.csv
#
# Generate input.csv using the following AppleScript and Things3 (the
# unregistered version works too). If you're using Things2, just install the
# Things3 demo and import Things2 data:
# https://gist.github.com/leonroy/5b764856d56990e1dbac
#
# If the import fails with INVALID_TEMPID, retry with a smaller CSV file, i.e.
# manually chunk it up into multiple smaller files. This is an issue of the
# Todoist API. :(

import todoist
import csv
import sys
import time

username = 'foo@example.com'
password = 'bar'
# Create a new app in the Todoist Developer Center, then copy and paste
# the development API key here.
# Don't ask me why this is needed in addition to the login credentials,
# but the todoist-python documentation is not really informative (and also
# very buggy...)
api_key = 'dfa3f9edca52c406047115059caaccb5c03bae1e'

class APIWrap():
    def __init__(self, user, password, api_key):
        self.api = todoist.TodoistAPI(api_key, cache=None)
        self.user = self.api.user.login(user, password)
        self.api.sync()

    def projExists(self, proj):
        if (proj == ''):
            return True
        for project in self.api['projects']:
            if project['name'] == proj:
                return True
        return False

    def getIdForProj(self, proj):
        for project in self.api['projects']:
            if project['name'] == proj:
                return project['id']
        return None

    def createProj(self, proj):
        self.api.commit(raise_on_error=True)
        project = self.api.projects.add(proj)
        print(project)
        self.api.commit(raise_on_error=True)
        assert(self.projExists(proj))

t = APIWrap(username, password, api_key)

if __name__ == '__main__':
    with open(sys.argv[1]) as csvfile:
        reader = csv.reader(csvfile)
        cnt = 0
        for line in reader:
            name = line[0]

            # This is the first line
            if name == 'name':
                continue

            status = line[1]
            tags = line[2]
            due = line[4]
            project = line[7]
            notes = line[14]

            if not t.projExists(project):
                print(" ====================== Creating project %s" % project)
                t.createProj(project)
                time.sleep(3)

            moreLabels = ""
            if tags != "":
                for tag in tags.split(", "):
                    moreLabels += " @" + tag

            print("Adding item '%s' (project='%s', id='%s')" %
                (name, project, t.getIdForProj(project)))

            item = t.api.items.add(name + " @Things" + moreLabels,
                t.getIdForProj(project), date_string=line[4],
                auto_parse_labels=True)

            if notes != '':
                print(" -> Adding note to item")
                note = t.api.notes.add(item['id'], notes)

            if status == "completed":
                item.complete()
            else:
                print("==COMMIT==")
                t.api.commit(raise_on_error=True)

            if cnt % 90 == 0:
                print("==COMMIT==")
                t.api.commit(raise_on_error=True)

            cnt = cnt + 1


        print("==COMMIT==")
        t.api.commit()
