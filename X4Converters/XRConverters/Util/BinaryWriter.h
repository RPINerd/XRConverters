#pragma once

class BinaryWriter
{
public:
                                BinaryWriter            ( Assimp::IOStream* pStream );

    Assimp::IOStream*           GetStream               () const;

    template < typename T >
    void                        Write                   ( const T& value )
    {
        Write ( &value, 1 );
    }

    template < typename T >
    void                        Write                   ( const T* pValue, int count )
    {
        _pStream->Write ( pValue, sizeof(T), count );
    }

    template < typename T >
    void                        Write                   ( const std::vector<T>& values )
    {
        if ( !values.empty () )
            Write ( values.data (), values.size () );
    }

    // Provide a non-template overload for std::string instead of an explicit
    // template specialization (specializations inside class scope are not
    // permitted by ISO C++). This performs the same behavior: write the
    // string length as an int followed by the raw characters.
    void                        Write                   ( const std::string& str )
    {
        Write<int> ( static_cast<int>(str.size ()) );
        if ( !str.empty () )
            Write ( str.data (), static_cast<int>(str.size ()) );
    }

private:
    Assimp::IOStream*           _pStream;
};
