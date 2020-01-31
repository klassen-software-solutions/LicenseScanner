Feature: No Dependencies
  Scenario: Scanning a directory with no dependencies
    When we scan the "NoDependencies" project
    Then "NoDependencies" will not contain an output file
