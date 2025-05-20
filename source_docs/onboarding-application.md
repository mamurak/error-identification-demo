# **AmlValidationService Technical Documentation**

## **Overview**

The **AmlValidationService** evaluates the anti-money laundering (AML) risk of customers by scoring them based on their identity attributes and checking against known watchlists. This is part of the customer onboarding KYC pipeline in a banking context.

---

## **API Endpoint**

**POST** `/`

### **Request Schema:**

* `customerId` (string)  
* `fullName` (string)  
* `nationalId` (string)  
* `birthDate` (date)

### **Response Fields:**

* `status`: `PASS` or `FAIL`  
* `riskScore`: Integer (0–100)  
* `riskLevel`: `LOW`, `MEDIUM`, `HIGH`  
* `matchedWatchlists`: Array of matching entries  
* `timestamp`: ISO-8601

---

## **Common Error Patterns**

### **1\. HTTP 400 Bad Request**

**Symptoms:**

* Malformed JSON or missing required fields

**Logs:**

```
ERROR [aml-service] - Missing required input: customerId
```

**Root Causes:**

* Client sends incomplete or improperly formatted payload

**Resolution:**

* Validate all required fields are included and types are correct

---

### **2\. HTTP 404 Not Found**

**Symptoms:**

* Endpoint returns 404

**Logs:**

```
WARN [platform-http] - No consumers available on endpoint: platform-http:/
```

**Root Causes:**

* Camel route not active or incorrectly mapped

**Resolution:**

* Check YAML DSL route definition, ensure `path: /` matches actual request URL

---

### **3\. HTTP 500 Internal Server Error**

**Symptoms:**

* Runtime failure during  external service dependency failure

**Logs:**

```
ERROR [camel] - Error evaluating choice block: java.lang.NullPointerException
```

**Root Causes:**

* Incorrect use of Camel Simple expressions (`random()` or string interpolation)  
* Unexpected downstream error

**Resolution:**

* Add fallback logic for downstream errors

---

## **Log Interpretation Guide**

| Log Pattern | Meaning | Suggested Action |
| ----- | ----- | ----- |
| `Evaluating AML validation outcome...` | Request successfully reached the route | Continue |
| `No consumers available` | Route is not registered for that path | Check Camel route URI |
| `NullPointerException` in mock logic | Incorrect JSON template or unquoted interpolation | Check indentation and syntax |

---

   
 

## **Contact**

Reach the AML Validation engineering team via `#aml-risk-devs` Slack channel or log a ticket in the `AML-SVC` JIRA project.

## **OpenAPI Spec**
```
openapi: 3.0.0  
info:  
  title: AML Validation Service  
  version: 1.0.0  
  description: \>  
    The AML Validation Service evaluates a customer's anti-money laundering (AML)  
    risk by scoring their identity details and matching them against watchlists.

paths:  
  /:  
    post:  
      summary: Validate a customer's AML risk profile  
      requestBody:  
        required: true  
        content:  
          application/json:  
            schema:  
              $ref: '\#/components/schemas/AmlValidationRequest'  
      responses:  
        '200':  
          description: AML check completed successfully  
          content:  
            application/json:  
              schema:  
                $ref: '\#/components/schemas/AmlValidationResponse'  
        '400':  
          description: Invalid input data  
          content:  
            application/json:  
              schema:
```

# **IdentityValidationService Technical Documentation**

## **Overview**

The **IdentityValidationService** is responsible for validating customer identity documents such as national IDs or passports. It is used in KYC (Know Your Customer) workflows in banking systems. The service exposes a REST endpoint `/validate` that accepts a JSON payload with customer identity details and returns a validation result.

---

## **API Endpoint**

**POST** `/validate`

### **Request Schema:**

* `customerId` (string)  
* `fullName` (string)  
* `nationalId` (string)  
* `birthDate` (date)

### **Response Fields:**

* `status`: `VERIFIED`, `FAILED`, or `REVIEW_REQUIRED`  
* `verificationScore`: integer (0–100)  
* `failureReason`, `reviewComment`: string (optional)  
* `timestamp`: ISO-8601

---

## **Common Error Patterns**

### **1\. HTTP 400 Bad Request**

**Symptoms:**

* Empty or malformed request payload  
* Missing required fields

**Logs:**

```
ERROR [validation] - Missing field 'nationalId'
ERROR [json] - Cannot deserialize value...
```

**Root Causes:**

* Client-side form submission error  
* Incorrect JSON formatting (e.g., using single quotes, missing commas)

**Resolution:**

* Ensure all required fields are populated  
* Validate request body using a linter or Postman before submitting

---

### **2\. HTTP 404 Not Found**

**Symptoms:**

* Service route is unreachable

**Logs:**

```
WARN [platform-http] - No consumers available on endpoint: platform-http:/validate
```

**Root Causes:**

* Camel REST route not correctly defined or not deployed  
* OpenShift Route misconfigured

**Resolution:**

* Confirm route configuration in Camel YAML DSL  
* Run `oc get routes` and verify exposed service path

---

### **3\. HTTP 500 Internal Server Error**

**Symptoms:**

* Service returns error with no obvious client fault

**Logs:**

```
ERROR [identity-service] - Unexpected exception occurred: java.lang.NullPointerException
ERROR [camel] - Error during route processing
```

**Root Causes:**

* Backend system (e.g., registry API) unavailable  
* Null reference in identity processing logic

**Resolution:**

* Add null checks and fallback values in route logic  
* Ensure downstream services are healthy

---

## **Log Interpretation Guide**

| Log Pattern | Meaning | Suggested Action |
| ----- | ----- | ----- |
| `Missing field 'X'` | Input JSON did not include a required field | Fix client request |
| `No consumers available` | No route matching the HTTP call | Check Camel route URI |
| `Error calling downstream service` | HTTP call to AML/KYC failed | Check URL, service availability |

---

---

## **Contact**

For production incidents, contact the Identity Validation Service team via `#kyc-platform-support` or raise a JIRA ticket in `BANK-IDVAL` project.

## IdentityValidationService OpenAPI
```
openapi: 3.0.0  
info:  
  title: Identity Validation Service  
  version: 1.0.0  
  description: API for verifying customer identity documents as part of banking KYC processes.

paths:  
  /validate:  
    post:  
      summary: Validate customer identity document  
      requestBody:  
        required: true  
        content:  
          application/json:  
            schema:  
              $ref: "\#/components/schemas/IdentityValidationRequest"  
      responses:  
        '200':  
          description: Identity validated successfully or failed with reason  
          content:  
            application/json:  
              schema:  
                $ref: "\#/components/schemas/IdentityValidationResponse"  
        '400':  
          description: Bad request – malformed JSON or missing fields  
          content:  
            application/json:  
              schema:  
                $ref: "\#/components/schemas/ErrorResponse"  
        '500':  
          description: Internal server error  
          content:  
            application/json:  
              schema:  
                $ref: "\#/components/schemas/ErrorResponse"

components:  
  schemas:  
    IdentityValidationRequest:  
      type: object  
      required:  
        \- customerId  
        \- fullName  
        \- nationalId  
        \- birthDate  
      properties:  
        customerId:  
          type: string  
          example: "CUST-102938"  
        fullName:  
          type: string  
          example: "Alice Smith"  
        nationalId:  
          type: string  
          example: "XYZ987654"  
        birthDate:  
          type: string  
          format: date  
          example: "1985-07-15"

    IdentityValidationResponse:  
      type: object  
      required:  
        \- customerId  
        \- status  
        \- verificationScore  
        \- timestamp  
      properties:  
        customerId:  
          type: string  
        status:  
          type: string  
          enum: \[VERIFIED, FAILED, REVIEW\_REQUIRED\]  
        identityType:  
          type: string  
          example: "NATIONAL\_ID"  
        documentNumber:  
          type: string  
          example: "XYZ1234567"  
        expiryDate:  
          type: string  
          format: date  
        fullName:  
          type: string  
        dateOfBirth:  
          type: string  
          format: date  
        verificationScore:  
          type: integer  
          format: int32  
          minimum: 0  
          maximum: 100  
        failureReason:  
          type: string  
          nullable: true  
        reviewComment:  
          type: string  
          nullable: true  
        timestamp:  
          type: string  
          format: date-time  
          example: "2025-05-15T07:45:00Z"

    ErrorResponse:  
      type: object  
      properties:  
        error:  
          type: string  
          example: "Service Unavailable"  
        message:  
          type: string  
          example: "Unable to process the request"  
        code:  
          type: string  
          example: "ID-SERVICE-500"  
        timestamp:  
          type: string  
          format: date-time
```