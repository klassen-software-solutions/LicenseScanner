Feature: Package Building
  Scenario: Bug 29 resources should be installed
    When we build the installation packages
    Then the source distribution should include the resources
     And the binary distribution should include the resources
