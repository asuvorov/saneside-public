Run: pylint
        --load-plugins pylint_django
        accounts/ api/ app/ core/ enrollment/ home/ hr/ templates/ settings.py
        settings_local.py settings_tests.py urls.py wsgi.py
        --rcfile=../pylint.conf --files-output=n
        --reports=y > reports/pylint.report
