import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    jprob = 1
    # for each person
    for person in people:
        # calculate the prob for that person
        person_prob = 1
        # find parents
        mother = people[person]['mother']
        father = people[person]['father']
        mother_genes = find_genes(mother, two_genes, one_gene)
        father_genes = find_genes(father, two_genes, one_gene)
        person_genes = find_genes(person, two_genes, one_gene)
        # note if they have trait
        person_trait = person in have_trait

        # If person has no parents, use standard gene probability- PROBS["gene"]
        if not mother and not father:
            jprob *= PROBS["gene"][person_genes]
        else:
            mother_prob = parent_prob(mother_genes)
            father_prob = parent_prob(father_genes)

            if person_genes == 2:
                person_prob *= mother_prob * father_prob
            elif person_genes == 1:
                person_prob *= (1 - mother_prob) * father_prob + \
                    (1 - father_prob) * mother_prob
            else:
                person_prob *= (1 - mother_prob) * (1 - father_prob)

        # Multiply by the probability of the person with X genes having / not having the trait:
        person_prob *= PROBS['trait'][person_genes][person_trait]

        jprob *= person_prob

    return jprob
#    raise NotImplementedError


def find_genes(person, two_genes, one_gene):
    # return the number of genes the person has
    if person in two_genes:
        return 2
    elif person in one_gene:
        return 1
    else:
        return 0


def parent_prob(parent_genes):
    # return the parent probablity based on their genes
    if parent_genes == 2:
        return 1 - PROBS['mutation']
    # if parents have one gene 50 percent chance
    elif parent_genes == 1:
        return 0.5
    # if no genes than just .01
    else:
        return PROBS['mutation']


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
#    print(f"{probabilities}")
    for person in probabilities:
        person_genes = find_genes(person, two_genes, one_gene)
        # note if they have trait
        person_trait = person in have_trait
        # update the probabilites
        probabilities[person]['gene'][person_genes] += p
        probabilities[person]['trait'][person_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Iterate over all people:
    for person in probabilities:

        # Calculate the total probability for each distribution
        gene_prob_sum = sum(probabilities[person]['gene'].values())
        trait_prob_sum = sum(probabilities[person]['trait'].values())

        # Normalise each distribution to 1:
        for akey in probabilities[person]['gene']:
            nprob = probabilities[person]['gene'][akey]/gene_prob_sum
            probabilities[person]['gene'].update({akey: nprob})
        for tkey in probabilities[person]['trait']:
            nprob = probabilities[person]['trait'][tkey]/trait_prob_sum
            probabilities[person]['trait'].update({tkey: nprob})


if __name__ == "__main__":
    main()
