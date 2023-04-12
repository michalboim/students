function User(){
    const [user, setUser] = React.useState('');
    const getUser = () => {
        axios.get('/user_detail').then((result) => {
            console.log(result.data)
            setUser(result.data.name);
        })
    }
    React.useEffect(() =>{
        getUser();}
        , [] 
        )
        return (
            <div class='hello_admin'>
                Hello {user}- what do you want to do?
            </div>
        );
}
ReactDOM.render(<User/>, document.getElementById('helloAdmin'))