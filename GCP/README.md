# GCP Migration Deployment – Employee Directory Application

This folder contains the Google Cloud Platform (GCP) implementation of the Employee Directory Demo Application. It represents the target environment for cloud migration from AWS to GCP.

The goal of this deployment is to recreate the application’s full functionality using GCP-native managed services, while maintaining infrastructure parity with the original AWS design.

## Overview

This project provisions a complete GCP environment using Terraform, including:

- Compute platform  - Compute Engine 

- Managed database layer - Firestore

- Secure IAM identity model using service accounts

- Networking infrastructure - VPC, subnets, routes

- Load balancing setup

- Cloud Storage for static content or assets

- Cloud Monitoring & Logging

The Terraform scripts inside this folder are fully modular and designed for production-grade deployments.