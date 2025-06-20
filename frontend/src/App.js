import React from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import HomePage from './pages/HomePage';
import './App.css';

// Simplified AWS Amplify configuration
const amplifyConfig = {
  Auth: {
    Cognito: {
      userPoolId: process.env.REACT_APP_USER_POOL_ID || 'eu-west-1_XXXXXXXXX',
      userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID || 'xxxxxxxxxxxxxxxxxxxxxxxxxx',
      identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID || 'eu-west-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    }
  }
};

// Configure Amplify
Amplify.configure(amplifyConfig);

function App() {
  return (
    <div className="App">
      <Authenticator
        signUpAttributes={['email']}
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
          <HomePage user={user} signOut={signOut} />
        )}
      </Authenticator>
    </div>
  );
}

export default App;