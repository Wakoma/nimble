'''
author: kny5,
email: antonio.anaya@kny5.work,
description: This script downloads and builds a docker image for the nimble cadorchestrator,
for development purposes, it uses a list of repositories defined in a dictionary format.

Requirements:
git
docker
ssh privileges to repositories are optional
'''


import sys
import os
import logging


print('\nCADOrchestrator Development environment setup. \nWakoma Inc. 2025. \nhttps://wakoma.co\n')

# setup logging messages format and level
logger = logging.getLogger(__name__)
stdout_log_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s'
)
stdout_log_handler = logging.StreamHandler(stream=sys.stdout)
stdout_log_handler.setLevel(logging.INFO)
stdout_log_handler.setFormatter(stdout_log_formatter)
logger.addHandler(stdout_log_handler)
logger.setLevel(logging.INFO)

# check if git and docker are installed
print("Checking dependencies...\n")
try:
    os.system('git --version')
    os.system('docker --version')
except OSError as e:
    logger.error(e)

# Repositories to download and use for Docker image
REPOSITORIES = [{
'author': 'kny5',
'repository': 'cq-cli',
'local_name': 'cq-cli-nimble',
'select_branch':'server_hotfix_01',
'https_url':'https://github.com/kny5/cq-cli.git',
'git_url':'git@github.com:kny5/cq-cli.git'},{

'author': 'gitbuilding',
'repository': 'cadorchestrator', 
'local_name': 'cadorchestrator',
'select_branch':'server_hotfix_01',
'https_url':'https://gitlab.com/gitbuilding/cadorchestrator.git',
'git_url':'git@gitlab.com:gitbuilding/cadorchestrator.git'},{

'author': 'Wakoma',
'repository': 'nimble', 
'local_name': 'nimble',
'select_branch':'server_hotfix_01',
'https_url':'https://github.com/Wakoma/nimble.git',
'git_url':'git@github.com:Wakoma/nimble.git'}]

# dockerfile and docker image names
DOCKERFILE_DEV = "docker/Dockerfile.dev"
IMAGE_NAME = "nimble_cadorch_development"

# checking if dependencies repositories exists locally.
class DevSetUp:
    '''
    This program downloads and builds a docker image for the nimble cadorchestrator
    development environment
    '''

    @staticmethod
    def create_meta_dir():
        '''This method creates the meta directory for the nimble cadorchestrator,
        copying all the contents of nimble for easy containerisation.'''
        current_dir = os.path.basename(os.getcwd())

        if current_dir == 'nimble':
            os.chdir('dev')
            logger.warning("You are not allowed to re-create the meta directory.")
        else:
            logger.warning("")
        cmd = f'rsync -av --exclude="{current_dir}" ../ ./nimble'
        os.system(cmd)


    @staticmethod
    def set_repositories():
        '''
        This method sets the repositories used for development.
        See object_repositories for more details.
        '''

        privilege = input("\nDo you have SSH privileges to the repository? (y/n): ")

        if privilege == 'y':
            logger.info("This assumes you have setup API keys, "
                        "and ssh privileges to the git services.")
            url_type = "git_url"
        else:
            logger.warning("Using https_urls, you may need to setup your repository privilege "
                           "for pulling changes later.")
            url_type = "https_url"

        for repo in REPOSITORIES:
            if os.path.isdir(repo['local_name']):
                logger.warning("Local repo exists for: %s, %s",
                               repo['repository'], repo['local_name'])
                if privilege == 'y':
                    logger.warning("You may need to setup your repository privilege "
                                   "for push/pull changes later.")
            else:
                try:
                    os.system(f"git clone -b {repo['select_branch']} "
                              f"{repo[url_type]} {repo['local_name']}")
                    logger.info("Cloning repo for: %s, %s", repo['repository'], repo['local_name'])
                except OSError as e:
                    logger.error(e)
        logger.info("Development environment directories in place.")

    @staticmethod
    def check_image():
        '''This method checks if the docker image exists.'''
        logger.info("Checking image: %s", IMAGE_NAME)
        cmd = "docker inspect {img} | grep {img}".format(img = IMAGE_NAME)

        if os.system(cmd) == 1:
            return True

        return False

    @staticmethod
    def build_image():
        '''
        This method builds a docker image for the nimble cadorchestrator.
        You have the cache option (quicker) or nocache.
        '''
        cache_ops = ""
        current_dir = os.path.basename(os.getcwd())
        if not DevSetUp.check_image():
            docker = input(f"\nRe-build Docker development image {IMAGE_NAME}? (y/n): ")

            if docker == "y":
                cache = input("\nDo you want to use image cache? (y/n): ")
                if cache != 'y':
                    cache_ops = " --no-cache"
                try:
                    print("Building Docker development image... This may take a while...")
                    logger.info(str(os.system("ls")))
                    os.chdir('dev/nimble')
                    logger.info(str(os.system("ls")))
                    cmd = f"docker build {cache_ops} -t {IMAGE_NAME} -f {DOCKERFILE_DEV} . "
                    logger.info(cmd)
                    os.system(cmd)
                    os.chdir('dev')
                except OSError as e:
                    logger.error(e)

        else:
            cmd = f"docker build {cache_ops} -t {IMAGE_NAME} -f {DOCKERFILE_DEV} . "
            logger.info(cmd)
            os.system(cmd)

    @staticmethod
    def run_image():
        '''This method runs the docker image build.'''
        if not DevSetUp.check_image():
            run_img = input("\nDo you want to run the image? (y/n): ")
            if run_img == 'y':
                cmd = f"docker run -p 8001:8000 {IMAGE_NAME}"
                logger.info(cmd)
                os.system(cmd)
            else:
                print("\nNothing to do.\n")
                logger.info("Exiting...")

if __name__ == "__main__":
    try:
        DevSetUp.create_meta_dir()
        DevSetUp.set_repositories()
        DevSetUp.build_image()
        DevSetUp.run_image()
    except OSError as e:
        logger.error(e)
    except KeyboardInterrupt:
        logger.error("\nProgram interrupted...")
