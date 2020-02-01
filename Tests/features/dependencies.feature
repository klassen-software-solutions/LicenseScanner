Feature: Dependency Tracking
  Scenario: Project with no dependencies
    When we scan the "NoDependencies" project
    Then there should be no output file

  Scenario: Project with manual dependencies
    When we scan the "ManualDependencies" project
    Then there should be an output file
     And there should be 2 modules
     And module "libuuid" should have a "BSD 3-Clause \"New\" or \"Revised\" License" license with a "BSD-3-Clause" spdx entry
     And module "rabbitmq" should have a "Mozilla Public License 1.1" license with a "MPL-1.1" spdx entry
