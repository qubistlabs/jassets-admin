builder(
        jUnitReportsPath: 'junit-reports',
        buildTasks: [
                [
                        name: "Linters",
                        type: "lint",
                        method: "inside",
                        runAsUser: "root",
                        entrypoint: "",
                        jUnitPath: '/junit-reports',
                        command: [
                                'pip install --no-cache-dir --src=/src/ -r requirements.txt',
                                'mkdir -p /junit-reports',
                                'py.test --pylama --junit-xml /junit-reports/pylama-report.xml',
                        ],
                ],
        ],
        slackTargetNames: '#radio-jticker',
        slackNotificationBranchFilter: '.*',
)
