#!/usr/bin/env python

from getpass import getpass

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--superuser', action='store_true',
            help="Creates a superuser.", )
        parser.add_argument('-u', '--username', type=str,
            help="Username of the superuser.", )
        parser.add_argument('-e', '--email', type=str,
            help="E-mail of the superuser.", )
        parser.add_argument('-t', '--teamname', type=str,
            help="Team to which add the superuser.", )
        parser.add_argument('-p', '--password', type=str,
            help="Password of the superuser.", )

    def handle(self, *args, **kwargs):
        username = kwargs.get("username")

        if not username:
            username = input("Username: ")

        if not username:
            self.stdout.write(self.style.ERROR("Username cannot be blank."))
            exit()

        email = kwargs.get("email")

        if not email:
            email = input("E-mail: ")

        if not email:
            self.stdout.write(self.style.ERROR("E-mail cannot be blank."))
            exit()

        teamName = kwargs.get("teamname")

        if not teamName:
            teamName = input("Team: ")

        if not teamName:
            self.stdout.write(self.style.ERROR("Team cannot be blank."))
            exit()

        password = kwargs.get("password")
        if not password:
            password = getpass()
            if not password:
                self.stdout.write(self.style.ERROR(
                    "Password cannot be blank."))
                exit()
            if password != getpass(prompt='Confirm password: '):
                self.stdout.write(self.style.ERROR(
                    "Passwords do not match."))
                exit()

        try:
            grp = Group.objects.get(name=teamName)
            self.stdout.write(self.style.WARNING(
                "Group '{}' already exists!".format(teamName)))
        except Group.DoesNotExist:
            self.stdout.write("Creating group '{}'".format(teamName))
            grp = Group.objects.create(name=teamName)
            grp.save()
            self.stdout.write(self.style.SUCCESS(
                "Group '{}' successfully created!".format(teamName)))

        try:
            usr = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(
                "User '{}' already exists!".format(username)))
        except User.DoesNotExist:
            if kwargs.get("superuser"):
                self.stdout.write("Creating superuser '{}'".format(username))
                usr = User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(
                    "Superuser '{}' successfully created!".format(username)))
            else:
                self.stdout.write("Creating user '{}'".format(username))
                usr = User.objects.create_user(username, email, password)
                self.stdout.write(self.style.SUCCESS(
                    "User '{}' successfully created!".format(username)))

        if usr.groups.filter(name=teamName).count() == 0:
            self.stdout.write("Adding user '{}' to group '{}'".format(
                username, teamName))
            usr.groups.add(grp)
            usr.save()
            self.stdout.write(self.style.SUCCESS(
                "User '{}' successfully added to group '{}'!".format(
                    username, teamName)))
        else:
            self.stdout.write(self.style.WARNING(
                "User '{}' already in group '{}'!".format(
                    username, teamName)))
