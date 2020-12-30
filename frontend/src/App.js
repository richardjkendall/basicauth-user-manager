import React, { Component } from 'react';

import { Grommet, Box, Heading, Text, TextInput, Button, Menu, Layer } from 'grommet';
import { Menu as MenuIcon, Next, Previous } from 'grommet-icons'
import { grommet } from "grommet/themes";

import './App.css';

const Header = (props) => (
  <Box
    tag='header'
    background='brand'
    pad='small'
    elevation='small'
    justify='between'
    direction='row'
    align='center'
    flex={false}
  >
    <Heading level={3} margin='none'>
      <strong>User Manager</strong>
    </Heading>
    <Menu
      dropAlign={{ top: 'bottom', right: 'right' }}
      items={[
        { label: "Logged in as " + props.userName, disabled: true },
        { label: "Logout", onClick: () => {
          // need to logout
          props.logout();
        } }
      ]}
      icon={<MenuIcon color='white' />}
    />
    
  </Box>
);

const Footer = (props) => (
  <Box
    tag='footer'
    direction='row'
    justify='end'
    pad='medium'
    border={{ side: 'top' }}
    gap='small'
    flex={false}
  >
    <Button label='Remove' color='border' onClick={() => {props.remove()}} />
    <Button label='Add' primary={true} onClick={() => {props.add()}} />
  </Box>
);

class App extends Component { 
  constructor(props) {
    super(props)
  } 

  componentDidMount() {

  }

  render() {
    return(
      <Grommet theme={grommet} full={true}>
        <Box fill={true}>
          <Header userName={"blah"} logout={() => {}} />

          <Footer 
              add={() => {}} 
              remove={() => {}}
            />
        </Box>
      </Grommet>
    )
  }
}

export default App;
