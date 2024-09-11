# PlanktonAPI

An asynchronous template for modern FastAPI backends to go from Design to Deployment ASAP.

## Overview

PlanktonAPI is designed with simplicity and efficiency in mind. The goal is to create a fast, scalable, and secure backend for most modern apps by focusing on just three core files: `app.py`, `models.py`, and `schema.py` (all located in the `app` directory).

### Key Features

- **Streamlined User Authentication**: 
  - Secure implementation without over-abstraction of user models.
  - Users are treated as standard database entities, simplifying customization and integration.

- **Fully Asynchronous Architecture**: 
  - Leverages FastAPI's asynchronous capabilities for high performance.
  - Includes asynchronous database operations for improved scalability.

- **Advanced Password Security**: 
  - Utilizes Argon2 for password hashing (winner of the 2015 Password Hashing Competition).
  - Provides robust protection against various types of password attacks.

- **Stateless JWT Authentication**: 
  - Implements JSON Web Tokens for secure, scalable authentication.
  - Eliminates the need for server-side session storage.

- **Modular and Maintainable Structure**: 
  - Clear separation of concerns with a focus on three main files.
  - Facilitates easy updates and extensions to the codebase.

- **Practical Helper Functions**: 
  - Includes utility functions like `get_current_user` for seamless user context retrieval.
  - Designed to simplify common backend tasks and reduce boilerplate code.

- **Pydantic Data Validation**: 
  - Leverages Pydantic for robust input/output data validation and serialization.
  - Ensures data integrity and reduces the likelihood of runtime errors.

## Philosophy

PlanktonAPI takes a pragmatic approach to user model implementation. By treating users as regular database entities alongside other models, it maintains consistency and simplifies the development process. This design choice makes it easier to get started quickly and allows for straightforward customization of user-related functionality.

The user model, schema, and related API endpoints are purposefully kept in the main editing area. This serves as a clear, practical example that developers can easily reference and replicate when creating additional data models and endpoints.

## Structure

The API endpoints in `app.py` are organized into three categories:

1. **Public**: Open endpoints such as user registration and login.
2. **Middle**: Endpoints requiring an API token but not inferring user context.
3. **Private**: Endpoints requiring both an API token and inferred user context.

Data validation for API requests and responses is handled by Pydantic, with schemas defined in `schemas.py`. This ensures type safety and helps prevent data-related bugs.

## Getting Started

1. Set up a virtual environment for your project.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your project by editing `settings.py` to match your requirements.
4. Focus on these three core files to build your backend logic:
   - `app/app.py`: Define your API endpoints and business logic.
   - `app/models.py`: Create your database models.
   - `app/schema.py`: Define Pydantic schemas for request/response validation.

## Customization

The power of PlanktonAPI lies in its simplicity. After the initial setup, you can create a full-featured backend by focusing on the three main files mentioned above. This approach streamlines the development process, allowing for rapid iteration and easy maintenance as your project grows.

## Contributing

Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
