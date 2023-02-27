      #!/bin/bash

      echo pythonVersion: "3.8.10"
      echo profile: "latest"
      echo fullTest: "True"
      echo module: ""
      echo Build.Reason: "PullRequest"
      serial_modules="vm"

	echo "Running full test"
	python scripts/ci/automation_full_test.py "8" "2" "latest" "$serial_modules"