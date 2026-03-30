# FortiMail API Python 

Local project fork for development

Python library to configure Fortinet's FortiMail devices (REST API)


To generate new version in PyPi do the following:

1. Submit all your changes including version update of ./setup.py to remote repo
2. Create a tag in the repo for this last commit
3. Push new tag into repo:
 
   git push --tags
4. Create new package: 

   python setup.py sdist 
   
5. Upload package: 
  
   twine upload dist/fortimailapi-0.x.x.tar.gz
   
   
Note: Ensure there is ~/.pypirc file with chmod 600 permissions and the following content:

            [distutils]
            index-servers =
              pypi
              pypitest
            
            [pypi]
            repository=https://upload.pypi.org/legacy/
            username=your_user
            password=your_password
            
            [pypitest]
            repository=https://testpypi.python.org/pypi
            username=your_user
            password=your_password
