import React from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import HomePage from './pages/HomePage';
import './App.css';

// Debug environment variables
console.log('Environment variables:', {
  userPoolId: process.env.REACT_APP_USER_POOL_ID,
  userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID,
  identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID,
  apiUrl: process.env.REACT_APP_API_URL,
  region: process.env.REACT_APP_AWS_REGION
});

// AWS Amplify configuration for v5
const amplifyConfig = {
  Auth: {
    region: process.env.REACT_APP_AWS_REGION || 'eu-west-1',
    userPoolId: process.env.REACT_APP_USER_POOL_ID || '',
    userPoolWebClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID || '',
    identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID || '',
    authenticationFlowType: 'USER_SRP_AUTH',
    oauth: {
      domain: '', // Not using OAuth for now
      scope: ['email', 'openid', 'profile'],
      redirectSignIn: window.location.origin,
      redirectSignOut: window.location.origin,
      responseType: 'code'
    }
  },
  API: {
    endpoints: [
      {
        name: 'catalogAPI',
        endpoint: process.env.REACT_APP_API_URL || 'http://localhost:5000',
        region: process.env.REACT_APP_AWS_REGION || 'eu-west-1'
      }
    ]
  }
};

// Only configure Amplify if we have the required environment variables
if (process.env.REACT_APP_USER_POOL_ID && process.env.REACT_APP_USER_POOL_CLIENT_ID) {
  try {
    Amplify.configure(amplifyConfig);
    console.log('✅ Amplify configured successfully');
  } catch (error) {
    console.error('❌ Error configuring Amplify:', error);
  }
} else {
  console.error('❌ Missing required Amplify environment variables');
  console.error('Required variables:', [
    'REACT_APP_USER_POOL_ID',
    'REACT_APP_USER_POOL_CLIENT_ID',
    'REACT_APP_IDENTITY_POOL_ID',
    'REACT_APP_AWS_REGION'
  ]);
}

// Custom form fields for better UX
const formFields = {
  signUp: {
    email: {
      order: 1,
      placeholder: 'Enter your email address',
      isRequired: true,
      label: 'Email Address'
    },
    password: {
      order: 2,
      placeholder: 'Enter your password (min 8 characters)',
      isRequired: true,
      label: 'Password'
    },
    confirm_password: {
      order: 3,
      placeholder: 'Confirm your password',
      isRequired: true,
      label: 'Confirm Password'
    }
  },
  signIn: {
    username: {
      placeholder: 'Enter your email address',
      isRequired: true,
      label: 'Email Address'
    },
    password: {
      placeholder: 'Enter your password',
      isRequired: true,
      label: 'Password'
    }
  }
};

function App() {
  // Check if Amplify is properly configured
  if (!process.env.REACT_APP_USER_POOL_ID || !process.env.REACT_APP_USER_POOL_CLIENT_ID) {
    return (
      <div style={{ 
        padding: '50px', 
        textAlign: 'center', 
        backgroundColor: '#f5f7fa',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <h1 style={{ color: '#dc2626', marginBottom: '20px' }}>Configuration Error</h1>
        <p style={{ fontSize: '16px', marginBottom: '20px' }}>
          AWS Amplify is not properly configured. Missing environment variables.
        </p>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          <h3 style={{ marginBottom: '15px' }}>Required Environment Variables:</h3>
          <ul style={{ textAlign: 'left', fontSize: '14px' }}>
            <li>REACT_APP_USER_POOL_ID: {process.env.REACT_APP_USER_POOL_ID ? '✅ Set' : '❌ Missing'}</li>
            <li>REACT_APP_USER_POOL_CLIENT_ID: {process.env.REACT_APP_USER_POOL_CLIENT_ID ? '✅ Set' : '❌ Missing'}</li>
            <li>REACT_APP_IDENTITY_POOL_ID: {process.env.REACT_APP_IDENTITY_POOL_ID ? '✅ Set' : '❌ Missing'}</li>
            <li>REACT_APP_AWS_REGION: {process.env.REACT_APP_AWS_REGION ? '✅ Set' : '❌ Missing'}</li>
            <li>REACT_APP_API_URL: {process.env.REACT_APP_API_URL ? '✅ Set' : '❌ Missing'}</li>
          </ul>
          <p style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
            Please check your deployment configuration and ensure environment variables are properly set.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Authenticator
        formFields={formFields}
        signUpAttributes={['email']}
        usernameAlias="email"
        variation="modal"
      >
        {({ signOut, user }) => (
          <HomePage user={user} signOut={signOut} />
        )}
      </Authenticator>
    </div>
  );
}

export default App;