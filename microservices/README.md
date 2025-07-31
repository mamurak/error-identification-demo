# Customer Onboarding Microservices

This folder contains four Quarkus-based microservices used for a customer onboarding demo. Each microservice is a standalone Maven project and can be independently built and deployed to an OpenShift cluster.

## 📦 Microservices List

- `customer-onboarding-service`
- `identity-verification-service`
- `risk-assessment-service`
- `notification-service`

Each of these services is located in its own subdirectory under `microservices/`.

---

## 🚀 Build and Deploy to OpenShift

Ensure that you are authenticated to your OpenShift cluster and have the appropriate project selected.

cd customer-onboarding-service
mvn clean install -Dquarkus.openshift.deploy=true

cd ../identity-verification-service
mvn clean install -Dquarkus.openshift.deploy=true

cd ../risk-assessment-service
mvn clean install -Dquarkus.openshift.deploy=true

cd ../notification-service
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
