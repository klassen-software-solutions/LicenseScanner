Feature: Dependency Tracking
  Scenario: Project with no dependencies
    When we scan the "NoDependencies" project
    Then there should be no output file

  Scenario: Project with manual dependencies
    When we scan the "ManualDependencies" project
     And we generate an HTML report
    Then there should be an output file
     And there should be 3 modules
     And the project should be used by 3 modules
     And module "libuuid" should be "BSD 3-Clause \"New\" or \"Revised\" License" with a "BSD-3-Clause" spdx id
     And module "rabbitmq" should be "Mozilla Public License 1.1" with a "MPL-1.1" spdx id
     And module "ksstest" should be "MIT License" with a "MIT" spdx id
     And there should be an HTML report
     And the HTML report should include an entry for each license

  Scenario: Project with KSS style dependencies
    When we scan the "KssDependencies" project
    Then there should be an output file
     And there should be 11 modules
     And the project should be used by 6 modules
     And module "ksstest" should be "MIT License" with a "MIT" spdx id
     And module "ksscontract" should be "MIT License" with a "MIT" spdx id
     And module "anotherdep" should be "MIT License" with a "MIT" spdx id
     And module "someproj" should be "BSD 4-Clause \"Original\" or \"Old\" License" with a "BSD-4-Clause" spdx id
     And module "requests" should be "Apache License 2.0" with a "Apache-2.0" spdx id
     And module "certifi" should be "Mozilla Public License 2.0" with a "MPL-2.0" spdx id
     And module "urllib3" should be "MIT License" with a "MIT" spdx id
     And module "chardet" should be "GNU Lesser General Public License v2.1 only" with a "LGPL-2.1" spdx id
     And module "idna" should be "BSD-like" with no spdx id
     And module "nolicensefile" should be "Unknown" with no spdx id
     And module "nodirectory" should be "Unknown" with no spdx id

  Scenario: Project with Swift style dependencies
    When we scan the "SwiftDependencies" project
    Then there should be an output file
     And there should be 3 modules
     And the project should be used by 2 modules
     And module "swift-nio" should be "Apache License 2.0" with a "Apache-2.0" spdx id
     And module "swift-nio-transport-services" should be "Apache License 2.0" with a "Apache-2.0" spdx id
     And module "Bug35" should be "Bug35 License" with no spdx id

  Scenario: Project combining all styles of dependencies
    When we scan the "MultiProject" project
    Then there should be an output file
     And there should be 9 modules
     And the project should be used by 6 modules
     And module "ksstest" should be "MIT License" with a "MIT" spdx id
     And module "ksscontract" should be "MIT License" with a "MIT" spdx id
     And module "requests" should be "Apache License 2.0" with a "Apache-2.0" spdx id
     And module "certifi" should be "Mozilla Public License 2.0" with a "MPL-2.0" spdx id
     And module "urllib3" should be "MIT License" with a "MIT" spdx id
     And module "chardet" should be "GNU Lesser General Public License v2.1 only" with a "LGPL-2.1" spdx id
     And module "rabbitmq" should be "Mozilla Public License 1.1" with a "MPL-1.1" spdx id
     And module "swift-nio" should be "Apache License 2.0" with a "Apache-2.0" spdx id
     And module "Bug35" should be "Bug35 License" with no spdx id
