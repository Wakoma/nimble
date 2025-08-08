'''
author: kny5,
email: antonio.anaya@kny5.work,
description: This script downloads and builds a docker image for the nimble cadorchestrator, for development purposes,
it uses a list of repositories defined in a dictionary format.

Requirements:
git
docker
ssh privileges to repositories are optional
'''


print('\nCADOrchestrator Development environment setup. \nWakoma Inc. 2025. \nhttps://wakoma.co\n')
import sys
import os
import logging

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
except Exception as e:
    logger.error(e)

# Repositories to download and use for Docker image
project_repositories = [{
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
dockerfile_dev = "cadorch_devops/docker/Dockerfile.dev"
image_name = "nimble_cadorch_development"

# checking if dependencies repositories exists locally.
class DevSetUp:
    print("\nThis program downloads and builds a docker image for the nimble cadorchestrator development environment.\n")
    print("Answer the following questions to continue:\n")

    def create_meta_dir(self):
        meta = input("\nDo you want to re-create the meta directory? "
                     "\nThe meta directory copies all the upper nimble directory content inside the dev environment. (y/n) ")
        if meta == 'y':
            current_dir = os.path.basename(os.getcwd())
            cmd = f'rsync -av --exclude="{current_dir}" ../ ./nimble'
            os.system(cmd)
        else:
            pass

    def set_repositories(self):
        privilege = input("\nDo you have SSH privileges to the repository? (y/n): ")

        if privilege == 'y':
            logger.info(f"This assumes you have setup API keys, and ssh privileges to the git services.")
            url_type = "git_url"
        else:
            logger.warning("Using https_urls, you may need to setup your repository privilege for pulling changes later.")
            url_type = "https_url"

        for repo in project_repositories:
            if os.path.isdir(repo['local_name']):
                logger.warning(f"Local repo exists for: {repo['repository']}, {repo['local_name']}")
                if privilege == 'y':
                    logger.warning("You may need to setup your repository privilege for push/pull changes later.")
                pass
            else:
                try:
                    os.system("git clone -b {branch} {url} {name}".format(url = repo[url_type], name = repo['local_name'], branch = repo['select_branch']))
                    logger.info(f"Cloning repo for: {repo['repository']}, {repo['local_name']}")
                except Exception as e:
                    logger.error(e)
        logger.info("Development environment directories in place.")


    def check_image(self):
        logger.info(f"Checking image: {image_name}")
        cmd = "docker inspect {img} | grep {img}".format(img = image_name)

        if os.system(cmd) == 1:
            return True
        else:
            return False

    def build_image(self):
        if not self.check_image():
            docker = input("\nDo you want to re-build Docker development image {img}? (y/n): ".format(img = image_name))

            if docker == "y":
                cache = input("\nDo you want to use image cache? (y/n): ")
                if cache != 'y':
                    cache_ops = " --no-cache"
                else:
                    cache_ops = ""
                try:
                    print("Building Docker development image... This may take a while...")
                    cmd = f"docker build {cache_ops} -t {image_name} -f {dockerfile_dev} . "
                    logger.info(cmd)
                    os.system(cmd)
                except Exception as e:
                    logger.error(e)

        else:
            cmd = f"docker build {cache_ops} -t {image_name} -f {dockerfile_dev} . "
            logger.info(cmd)
            os.system(cmd)


    def run_image(self):
        if not self.check_image():
            run_img = input("\nDo you want to run the image? (y/n): ")
            if run_img == 'y':
                cmd = f"docker run -p 8001:8000 {image_name}"
                logger.info(cmd)
                os.system(cmd)
            else:
                print("\nNothing to do.\n")
                logger.info("Exiting...")

if __name__ == "__main__":
    try:
        DevSetUp().create_meta_dir()
        DevSetUp().set_repositories()
        DevSetUp().build_image()
        DevSetUp().run_image()
    except Exception as e:
        logger.error(e)

