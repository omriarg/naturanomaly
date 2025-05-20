import React from "react";
import MainScreen from './components/MainScreen';
import ErrorBoundary from "./components/ErrorBoundary";

const App = () => {
  return (
    <ErrorBoundary>
      <MainScreen />
    </ErrorBoundary>
  );
};

export default App;
