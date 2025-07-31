# Customer Onboarding Microservices

This folder contains four Quarkus-based microservices used for a customer onboarding demo. Each microservice is a standalone Maven project and can be independently built and deployed to an OpenShift cluster.

## 📦 Microservices List

- `customer-onboarding-service`
- `customer-verification-service`
- `identity-validation-service`
- `AML-validation-service`

Each of these services is located in its own subdirectory under `microservices/`.

---

## 🚀 Build and Deploy to OpenShift

Ensure that you are authenticated to your OpenShift cluster and have the appropriate project selected.

cd CustomerOnboardingService
mvn clean install -Dquarkus.openshift.deploy=true

cd ../CustomerValidationService
mvn clean install -Dquarkus.openshift.deploy=true

cd ../IdentityValidationService
mvn clean install -Dquarkus.openshift.deploy=true

cd ../AmlValidationService
mvn clean install -Dquarkus.openshift.deploy=true

---

## 🚀 Post a new customer onboarding request

curl -v -X POST http://customer-onboarding-service-customer-onboarding.apps.<<ocp-domain.com>>/ \
-H "Content-Type: application/json" \
-d '{
   "customerId": "CUST-102938",
   "fullName": "Alice Smith",
   "nationalId": "XYZ987654",
   "birthDate": "1985-07-15"
}'
