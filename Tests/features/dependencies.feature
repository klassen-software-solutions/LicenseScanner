Feature: Dependency Tracking
  Scenario: Project with no dependencies
    When we scan the "NoDependencies" project
    Then there should be no output file

  Scenario: Project with manual dependencies
    When we scan the "ManualDependencies" project
    Then there should be an output file
     And there should be 3 modules
     And module "libuuid" should be "BSD 3-Clause \"New\" or \"Revised\" License" with a "BSD-3-Clause" spdx id
     And module "rabbitmq" should be "Mozilla Public License 1.1" with a "MPL-1.1" spdx id
     And module "ksstest" should be "MIT License" with a "MIT" spdx id
