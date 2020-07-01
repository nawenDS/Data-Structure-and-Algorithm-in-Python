class Tree:
    '''
    Abstract base class representing a tree structure
    '''
    #------------------Nested Position class---------------------------
    class Position:
        '''
        Abstract class representing the location of a single element
        '''
        def element(self):
            raise NotImplementedError('must be implemented by subclass')

        def __eq__(self, other):
            raise NotImplementedError('must be implemented by subclass')

        def __ne__(self, other):
            return not(self == other)

    #------Abstract methods that concrete subclass must support---------
    def root(self):
        raise NotImplementedError('must be implemented by subclass')

    def parent(self, p):
        raise NotImplementedError('must be implemented by subclass')

    def num_children(self, p):
        raise NotImplementedError('must be implemented by subclass')

    def children(self, p):
        raise NotImplementedError('must be implemented by subclass')

    def __len__(self):
        raise NotImplementedError('must be implemented by subclass')

    #----------------Concrete method implemented in this class---------
    def is_root(self, p):
        return self.root() == p

    def is_leaf(self, p):
        return self.num_children == 0

    def is_empty(self):
        return len(self) == 0
        
class BinaryTree(Tree):
    '''
    Abstract base class representing a binary tree structure
    '''

    #-----------------------additional abstract methods----------------

    def left(self, p):
        raise NotImplementedError('must be implemented by subclass')

    def right(self, p):
        raise NotImplementedError('must be implemented by subclass')

    #--------------------concrete methods implemented in this class----

    def sibling(self, p):
        parent = self.parent(p)
        if parent is None: # p must be root
            return None
        else:
            if p == self.left(parent):
                return self.right(parent)
            else:
                return self.left(parent)

    def children(self, p):
        '''
        Generate an iteration of Positions representing p's children
        '''
        if self.left(p) is not None:
            yield self.left(p)
        if self.right(p) is not None:
            yield self.right(p)


class LinkedBinaryTree(BinaryTree):
    '''
    Linked representation of a binary tree structure
    '''
    class _Node:
        '''
        Lightweight, nonpublic class for storing a node
        '''
        __slots__ = '_element','_parent','_left','_right'
        def __init__(self, element, parent = None, left = None, right = None):
            self._element = element
            self._parent = parent
            self._left = left
            self._right = right

    class Position(BinaryTree.Position):
        '''
        Abstraction representing the location of a single element
        Wraps a node
        '''
        def __init__(self, container, node):
            # constructor should not be invoked by user
            self._container = container
            self._node = node

        def element(self):
            return self._node._element

        def __eq__(self, other):
            return type(other) is type(self) and other._node is self._node

    def _validate(self, p):
        # robustly checking the validity of a given position instance
        # when unwrapping it.
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper Position type')
        if p._container is not self:
            raise ValueError('p does not belong to this container')
        # For deprecated node
        if p._node._parent is p._node:
            raise ValueError('p is no longer valid')
        return p._node

    def _make_position(self, node):
        # wrapping a node as a position to return to a caller
        return self.Position(self, node) if node is not None else None

    #-----------------------binary tree constructor--------------------

    def __init__(self):
        self._root = None
        self._size = 0

    #-----------------------public accessors----------------------------

    def __len__(self):
        return self._size

    def root(self):
        return self._make_position(self._root)

    def parent(self, p):
        node = self._validate(p)
        return self._make_position(node._parent)

    def left(self, p):
        node = self._validate(p)
        return self._make_position(node._left)

    def right(self, p):
        node = self._validate(p)
        return self._make_position(node._right)

    def num_children(self, p):
        node = self._validate(p)
        count = 0
        if node._left is not None:
            count += 1
        if node._right is not None:
            count += 1
        return count

    #-----------------------Nonpublic update-----------------------------
    def _add_root(self, e):
        '''
        Place element e at the root of an empty tree and return new Position
        Raise ValueError if tree nonempty
        '''
        if self._root is not None:
            raise ValueError('Root exists')
        self._size = 1
        self._root = self._Node(e)
        return self._make_position(self._root)

    def _add_left(self, p, e):
        node = self._validate(p)
        if node._left is not None:
            raise ValueError('Left child exists')
        self._size += 1
        node._left = self._Node(e, node)
        return self._make_position(node._left)

    def _add_right(self, p, e):
        node = self._validate(p)
        if node._right is not None:
            raise ValueError('Right child exists')
        self._size += 1
        node._right = self._Node(e, node)
        return self._make_position(node._right)

    def _replace(self, p, e):
        '''
        Replace the element at position p with e, and return old element
        '''
        node = self._validate(p)
        old = node._element
        node._element = e
        return old

    def _delete(self, p):
        '''
        Delete the node at Position p, and replace it with its child, if any
        Return the element that had been stored at Position p
        Raise ValueError if Position p is invalid or has two children
        '''
        node = self._validate(p)
        if self.num_children(p) == 2:
            raise ValueError('p has two children')
        # Might be None
        child = node._left if node._left else node._right
        if child is not None:
            child._parent = node._parent
        if node is self._root:
            self._root = child
        else:
            parent = node._parent
            if node is parent._left:
                parent._left = child
            else:
                parent._right = child
        self._size -= 1
        # Convention for deprecated node
        node._parent = node
        return node._element

    def _attach(self, p, t1, t2):
        '''
        Attach tree t1 and t2 as left and right subtrees of external p
        '''
        node = self._validate(p)
        if not self.is_leaf(p):
            raise ValueError('position must be leaf')
        if not type(self) is type(t1) is type(t2):
            raise TypeError('Tree types must match')
        self._size += len(t1) + len(t2)
        if not t1.is_empty():
            t1._root._parent = node
            node._left = t1._root
            # set t1 instance to empty
            t1._root = None
            t1._size = 0
        if not t2.is_empty():
            t2._root._parent = node
            node._right = t2._root
            t2._root = None
            t2._size = 0
