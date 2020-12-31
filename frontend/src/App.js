import React, { Component } from 'react';
import { Grommet, Box, Heading, Text, TextInput, Button, Menu, Layer, Select, FormField, DataTable } from 'grommet';
import { Menu as MenuIcon, Next, Previous } from 'grommet-icons'
import { grommet } from "grommet/themes";

import ApiHandler from './Api';

import './App.css';

const RealmList = (props) => {
  const [value, setValue] = React.useState("");

  return (
    <FormField label="Select realm">
      <Select
        options={props.options}
        value={props.selectedRealm}
        onChange={({option}) => props.updateRealm(option)}
      />
    </FormField>
  )
}

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

const UserTable = (props) => {

  var rowProps = {};
  rowProps[props.selectedUser] = {
      background: "accent-1"
  }

  return (
    <Box>
      <DataTable
        columns={[
          {property: "user", header: "Username", search: true, sortable: false}
        ]}
        onClickRow={
          event => {
            props.selectUser(event.datum.user);
          }
        }
        primaryKey="user" 
        data={props.users}
        rowProps={rowProps}
        //onSearch={(event) => {this.props.updateSearch(event)}}
      />
    </Box>
  )
};

const AddUser = (props) => {
  const [user, setUser] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [repeatPassword, setRepeatPassword] = React.useState("");
  const [useSalt, setUseSalt] = React.useState(true);

  const [controlsDisabled, setControlsDisabled] = React.useState(false);
  const [userAdded, setUserAdded] = React.useState(false);
  const [error, setError] = React.useState("");

  const callAddUser = function() {
    console.log("in calladduser", user);
    if(user !== "") {
      setControlsDisabled(true);
      var apiClient = new ApiHandler();
      apiClient.addUser(user, password, useSalt, (data) => {
        console.log(data);
        setControlsDisabled(false);
        setUser("");
        setPassword("");
        setRepeatPassword("");
        setUseSalt(true)
        setError("");
        setUserAdded(true);
      }, () => {
        console.log("error adding user");
      });
    } else {
      setError("Username cannot be blank");
    }
  }

  const closeAddedSuccessWindow = function() {
    setUserAdded(false);
    
    props.success(user);
  }

  const closeAndClear = function() {
    setControlsDisabled(false);
    setUser("");
    setPassword("");
    setRepeatPassword("");
    setUseSalt(true)
    setError("");
    
    props.close();
  }

  return (
    <div>
      {props.open && (
        <Layer position="center" modal onClickOutside={closeAndClear} onEsc={closeAndClear}>
          <Box pad="medium" gap="small" width="large">
            <Heading level={3} margin="none">Add New User</Heading>
            
            {error!=="" && 
            <Text color="status-error">{error}</Text>}
            <Box 
              as="footer"
              gap="small"
              direction="row"
              align="center"
              justify="end"
              pad={{top: "medium", bottom: "small"}}
            >
              <Button 
                label="Cancel" 
                color="border" 
                onClick={closeAndClear} 
                disabled={controlsDisabled}
              />
              <Button
                label={
                  <Text color="white">
                    <strong>Add Link</strong>
                  </Text>
                }
                primary
                onClick={callAddUser}
                disabled={controlsDisabled}
              />
            </Box>
          </Box>
          
        </Layer>
      )}
    </div>
  )

};

class App extends Component { 
  constructor(props) {
    super(props);

    this.apiClient = new ApiHandler();

    this.state = {
      realms: [],
      selectedRealm: "",
      users: [],
      addUserOpen: false
    };
  } 

  openAddUserWindow() {
    this.setState({
      addUserOpen: true
    });
  }

  closeAddUserWindow() {
    this.setState({
      addUserOpen: false
    });
  }

  userAddSuccessCallback(user) {
    this.setState({
      addUserOpen: false
    });
  }

  componentDidMount() {
    // get realms
    this.apiClient.getRealms((data) => {
      this.setState({
        realms: data.data
      });
    }, () => {
      console.log("error getting realms");
    });
  }

  updateRealm(realm) {
    this.setState({
      selectedRealm: realm,
      selectedUser: "n/a"
    });
    this.apiClient.getUsers(realm, (data) => {
      console.log("users", data.data);
      this.setState({
        users: data.data
      });
    }, () => {
      console.log("error getting users");
    });
  }

  selectUser(user) {
    console.log("selecting user", user);
    this.setState({
      selectedUser: user
    });
  }

  render() {
    return(
      <Grommet theme={grommet} full={true}>
        <Box fill={true}>
          <Header userName={"blah"} logout={() => {}} />
          <Box flex={true} pad='medium' overflow='auto'>
            <Box flex={false}>
              <RealmList
                options={this.state.realms}
                selectedRealm={this.state.selectedRealm}
                updateRealm={this.updateRealm.bind(this)}
              />
              <Box pad={{ top: 'medium' }} gap='small'>
                <UserTable 
                  users={this.state.users}
                  selectedUser={this.state.selectedUser}
                  selectUser={this.selectUser.bind(this)}
                />
              </Box>
            </Box>
          </Box>
          <Footer 
              add={this.openAddUserWindow.bind(this)} 
              remove={() => {}}
            />
        </Box>
        <AddUser
          open={this.state.addUserOpen}
          close={this.closeAddUserWindow.bind(this)}
          success={this.userAddSuccessCallback.bind(this)}
        />
      </Grommet>
    )
  }
}

export default App;
