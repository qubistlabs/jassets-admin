builder(
        jUnitReportsPath: 'junit-reports',
        coverageReportsPath: 'coverage-reports',
        buildTasks: [
                [
                        name: "Linters",
                        type: "lint",
                        method: "inside",
                        runAsUser: "root",
                        entrypoint: "",
                        jUnitPath: '/junit-reports',
                        command: [
                                'pip install --no-cache-dir --src=/src/ -r requirements-dev.txt',
                                'mkdir -p /junit-reports',
                                'py.test --pylama --pylama-only --junit-xml /junit-reports/pylama-report.xml',
                                'echo "Validate swagger spec..."',
                        ],
                ],
        ],
)
