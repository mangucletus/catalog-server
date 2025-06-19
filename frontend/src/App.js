import React, { useEffect, useState } from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import HomePage from './pages/HomePage';
import './App.css';

// AWS Amplify configuration
// Replace these values with your actual AWS Cognito settings
const amplifyConfig = {
  Auth: {
    Cognito: {
      userPoolId: process.env.REACT_APP_USER_POOL_ID || 'eu-west-1_XXXXXXXXX',
      userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID || 'xxxxxxxxxxxxxxxxxxxxxxxxxx',
      identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID || 'eu-west-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    }
  },
  API: {
    REST: {
      catalogAPI: {
        endpoint: process.env.REACT_APP_API_URL || 'http://localhost:5000',
        region: process.env.REACT_APP_AWS_REGION || 'eu-west-1'
      }
    }
  }
};

// Configure Amplify
Amplify.configure(amplifyConfig);

function App() {
  return (
    <div className="App">
      {/* AWS Cognito Authenticator component */}
      <Authenticator
        // Custom sign up fields
        signUpAttributes={['email']}
        
        // Custom form fields configuration
        formFields={{
          signUp: {
            email: {
              order: 1,
              placeholder: 'Enter your email address',
              isRequired: true,
            },
            password: {
              order: 2,
              placeholder: 'Enter your password',
              isRequired: true,
            },
            confirm_password: {
              order: 3,
              placeholder: 'Confirm your password',
              isRequired: true,
            }
          }
        }}
      >
        {({ signOut, user }) => (
          <main>
            {/* Pass user info and signOut function to HomePage */}
            <HomePage user={user} signOut={signOut} />
          </main>
        )}
      </Authenticator>
    </div>
  );
}

export default App;