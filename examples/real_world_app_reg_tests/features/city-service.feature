@rest
Feature: REST API example - City Service
  Scenario: Get City metadata by Name
    Given the REST API is configured with RestAgent
    When I send a GET request to "city/Shanghai"
    Then the response status code should be 200
    And the JSON path "countryCode" should equal "CHN"
    And the JSON path "population" should equal "9996300"
